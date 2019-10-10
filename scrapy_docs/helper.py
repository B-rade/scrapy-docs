import json

if __name__ == '__main__':
    with open('results/root.json', 'r') as file:
        root = json.load(file)

    good_urls = [response['url'] for response in root if response['status'] == 200]
    bad_urls = [response['url'] for response in root if response['status'] != 200]

    with open('results/start.json', 'w') as file:
        json.dump(good_urls, file)
    with open('results/fix.json', 'w') as file:
        json.dump(bad_urls, file)
