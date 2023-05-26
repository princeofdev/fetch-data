import requests
from datetime import datetime, timedelta
import sys

# Replace 'YOUR_API_KEY' with your actual API key from http://xbrl.us
API_KEY = 'YOUR_API_KEY'

def fetch_reports(ticker, num_reports):
    base_url = 'http://xbrl.us/api/v1/fact/search'
    headers = {'Authorization': f'Bearer {API_KEY}'}
    today = datetime.now().strftime('%Y-%m-%d')

    report_types = ['8-K', '10-K', '10-Q']
    for report_type in report_types:
        query_params = {
            'fields': 'report.date',
            'entity.ticker': ticker,
            'fact.hasExtension': 'false',
            'concept.localName': report_type,
            'report.period.fiscalYear': '',
            'report.period.fiscalPeriod': '',
            'fields': 'fact.links[\'document\']',
            'fact.ultimus': 'true',
            'fields': 'fact.dimension.us-gaap:DocumentType',
            'report.isMostRecent': 'true',
            'count': num_reports
        }
        response = requests.get(base_url, params=query_params, headers=headers)
        if response.status_code == 200:
            reports = response.json()['data']
            for report in reports:
                report_date = datetime.strptime(report['report.date'], '%Y-%m-%d')
                report_date_str = report_date.strftime('%Y-%m-%d')
                pdf_url = report['fact.links']['document'][0]['url']
                pdf_response = requests.get(pdf_url)
                if pdf_response.status_code == 200:
                    pdf_filename = f'{ticker}_{report_date_str}_{report_type}.pdf'
                    with open(pdf_filename, 'wb') as pdf_file:
                        pdf_file.write(pdf_response.content)
                        print(f'Saved {pdf_filename}')
                else:
                    print(f'Failed to download PDF for {ticker} {report_type} on {report_date_str}')
        else:
            print(f'Failed to fetch {report_type} reports for {ticker}')

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print('Usage: script.py TICKER NUM_REPORTS')
        sys.exit(1)
    ticker = sys.argv[1]
    num_reports = int(sys.argv[2])
    fetch_reports(ticker, num_reports)
