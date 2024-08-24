
import json
import sys
import urllib.parse
import argparse
from collections import OrderedDict
import asyncio
import aiohttp
import tempfile
import os
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

async def fetch_content(url, session, verbose):
    try:
        async with session.get(url, timeout=30) as response:
            response.raise_for_status()
            content = await response.text()
            if verbose:
                logging.info(f"Fetched: {url}")
            return content
    except aiohttp.ClientError as e:
        logging.error(f"Client error fetching {url}: {str(e)}", exc_info=verbose)
    except asyncio.TimeoutError:
        logging.error(f"Timeout fetching {url}")
    except Exception as e:
        logging.error(f"Unexpected error fetching {url}: {str(e)}", exc_info=verbose)
    return None

async def run_collectjuices(url, mode, session, verbose):
    content = await fetch_content(url, session, verbose)
    if content is None:
        return []

    with tempfile.NamedTemporaryFile(mode='w+', delete=False) as temp_file:
        temp_file.write(content)
        temp_file_path = temp_file.name

    cmd = f"jsluice {mode} -R '{url}' {temp_file_path}"
    if verbose:
        logging.info(f"Running command: {cmd}")

    try:
        proc = await asyncio.create_subprocess_shell(
            cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await proc.communicate()

        if stderr and verbose:
            logging.error(f"Error processing {url}: {stderr.decode()}")
        return stdout.decode().splitlines()
    except Exception as e:
        logging.error(f"Error running CollectJuices on {url}: {str(e)}", exc_info=verbose)
        return []
    finally:
        os.unlink(temp_file_path)  # Ensure temporary file is deleted

def is_js_file(url):
    return url.lower().endswith('.js')

def normalize_url(url, base_url):
    if url.startswith('//'):
        return 'https:' + url
    elif not url.startswith(('http://', 'https://')):
        return urllib.parse.urljoin(base_url, url)
    return url

async def process_collectjuices_output(jsluice_output, current_url, verbose):
    js_urls = set()
    non_js_urls = set()
    secrets = []
    for line in jsluice_output:
        try:
            data = json.loads(line)
            if 'url' in data:
                url = normalize_url(data['url'], current_url)
                parsed_url = urllib.parse.urlparse(url)
                new_url = urllib.parse.urlunparse((
                    parsed_url.scheme,
                    parsed_url.netloc,
                    parsed_url.path,
                    parsed_url.params,
                    parsed_url.query,
                    parsed_url.fragment
                ))
                (js_urls if is_js_file(new_url) else non_js_urls).add(new_url)
            elif 'kind' in data:
                data['original_file'] = current_url
                secrets.append(data)
        except json.JSONDecodeError:
            logging.error(f"Error decoding JSON: {line}", exc_info=verbose)

    if verbose:
        logging.info(f"Processed {current_url}: {len(js_urls)} JS URLs, {len(non_js_urls)} non-JS URLs, {len(secrets)} secrets")

    return js_urls, non_js_urls, secrets

async def recursive_process(initial_url, session, processed_urls, verbose):
    if initial_url in processed_urls:
        return set(), set(), []
    processed_urls.add(initial_url)

    urls_output = await run_collectjuices(initial_url, 'urls', session, verbose)
    secrets_output = await run_collectjuices(initial_url, 'secrets', session, verbose)

    js_urls, non_js_urls, secrets = await process_collectjuices_output(urls_output + secrets_output, initial_url, verbose)

    tasks = [
        recursive_process(url, session, processed_urls, verbose)
        for url in js_urls if url not in processed_urls
    ]

    results = await asyncio.gather(*tasks)

    for result_js_urls, result_non_js_urls, result_secrets in results:
        js_urls.update(result_js_urls)
        non_js_urls.update(result_non_js_urls)
        secrets.extend(result_secrets)

    return js_urls, non_js_urls, secrets

def severity_to_int(severity):
    severity_map = {'critical': 4, 'high': 3, 'medium': 2, 'low': 1, 'info': 0}
    return severity_map.get(severity.lower(), -1)

async def main():
    parser = argparse.ArgumentParser(description="CollectJuices - The Ultimate URL and Secrets Extractor")
    parser.add_argument('-m', '--mode', choices=['endpoints', 'secrets', 'both'], default='both',
                        help="Specify what to hunt for: endpoints, secrets, or both (default: both)")
    parser.add_argument('-v', '--verbose', action='store_true',
                        help="Enable verbose output")
    args = parser.parse_args()

    all_urls = set()
    all_secrets = []
    processed_urls = set()

    async with aiohttp.ClientSession() as session:
        tasks = [
            recursive_process(initial_url.strip(), session, processed_urls, args.verbose)
            for initial_url in sys.stdin if initial_url.strip()
        ]

        results = await asyncio.gather(*tasks)

        for js_urls, non_js_urls, secrets in results:
            all_urls.update(non_js_urls)
            all_secrets.extend(secrets)

    if args.mode in ['endpoints', 'both']:
        for url in sorted(all_urls):
            print(url)

    if args.mode in ['secrets', 'both']:
        sorted_secrets = sorted(all_secrets, key=lambda x: (-severity_to_int(x['severity']), json.dumps(x)))
        unique_secrets = list(OrderedDict((json.dumps(secret), secret) for secret in sorted_secrets).values())

        for secret in unique_secrets:
            print(json.dumps(secret))

if __name__ == "__main__":
    asyncio.run(main())
