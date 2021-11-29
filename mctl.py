"""
mctl: Mailchimp Top Links

Exports top links from Mailchimp campaigns sent over the specified period to
CSV.

Copyright 2021, Console Ltd https://console.dev
SPDX-License-Identifier: AGPL-3.0-or-later
"""

import datetime
import csv
from urllib.parse import urlparse
import click
import mailchimp_marketing as MailchimpMarketing
from mailchimp_marketing.api_client import ApiClientError


# Set up the CLI using click
# https://click.palletsprojects.com/en/8.0.x/documentation/
@click.command()
@click.option('--api_key', help='Mailchimp API key', required=True)
@click.option('--server', default='us7', help='Mailchimp server')
@click.option('--list_id', help='Mailchimp list ID', required=True)
@click.option('--since',
              help='Examine campaigns since this date (yyyy-mm-dd)', required=True)
@click.option('--before',
              help='Examine campaigns before this date (yyyy-mm-dd)', required=True)
@click.option('--minimum_clicks', default=200,
              help='Exclude links with fewer clicks than this')
def cli(api_key, server, list_id, since, before, minimum_clicks):
    """Exports top links from Mailchimp campaigns sent over the specified
    period to CSV."""

    # Create Mailchimp client
    try:
        mailchimp = MailchimpMarketing.Client()
        mailchimp.set_config({
            "api_key": api_key,
            "server": server
        })
        mailchimp.ping.get()
    except ApiClientError as error:
        click.echo(f"Error: {error.text}", err=True)

    # Parse the since and before dates
    since = datetime.datetime.strptime(since, '%Y-%m-%d')
    before = datetime.datetime.strptime(before, '%Y-%m-%d')

    # Get the list of campaigns from the Mailchimp API
    click.echo(f'Getting campaigns {since} - {before}')
    all_campaigns = get_campaigns(mailchimp, list_id, since, before)

    # Open CSV
    with click.open_file('clicks.csv', 'w') as csvfile:
        writer = csv.writer(csvfile)

        writer.writerow(['Campaign', 'URL', 'URL Clicks',
                        'Recipients', 'Ratio'])

        # Loop through each campaign and query Mailchimp's API for the links
        with click.progressbar(all_campaigns,
                               label=f'Counting links for {len(all_campaigns)} campaigns') as campaigns:
            for campaign in campaigns:
                click_details = get_click_details(
                    mailchimp, campaign['id'], minimum_clicks)
                # For each link we need to calculate a ratio of clicks
                # against the number of recipients. This allows us to compare
                # older newsletters with fewer subscribers, rather than just
                # the absolute click numbers.
                for url, clicks in click_details.items():
                    ratio = clicks / campaign['recipients']
                    writer.writerow(
                        [campaign['title'], url, clicks, campaign['recipients'], ratio])


def get_campaigns(mailchimp, list_id, since, before):
    """Get all campaigns for the specified list_id between the specified dates.

    Keyword arguments:
    mailchimp -- the Mailchimp API client (object)
    list_id -- the Mailchimp list ID (string)
    since -- since this date (datetime)
    before -- before this date (datetime)
    """

    campaigns = []

    try:
        campaign_results = mailchimp.campaigns.list(
            list_id=list_id,
            status='sent',
            since_send_time=since.isoformat(),
            before_send_time=before.isoformat(),
            count=1000  # Set to maximum value
        )

    except ApiClientError as error:
        click.echo(f"Error: {error.text}", err=True)

    # Loop through the campaigns and construct a list of the fields we want
    for result in campaign_results['campaigns']:
        campaign = {}
        campaign['id'] = result['id']
        campaign['title'] = result['settings']['title']

        if 'recipients' in result:
            campaign['recipients'] = result['recipients']['recipient_count']

        campaigns.append(campaign)

    return campaigns


def get_click_details(mailchimp, campaign_id, minimum_clicks):
    """Get click details on a URL basis for all clicked URLs in the specified
    campaign.

    Keyword arguments:
    mailchimp -- the Mailchimp API client (object)
    campaign_id -- the Mailchimp campaign ID (string)
    minimum_clicks -- excludes URLs that have fewer clicks that this (int)
    """

    clicks = {}

    try:
        click_results = mailchimp.reports.get_campaign_click_details(
            campaign_id=campaign_id,
            count=100)  # Never more than 100 links per campaign
    except ApiClientError as error:
        click.echo(f"Error: {error.text}", err=True)
        return []

    # Loop through all the URLs
    for detail in click_results['urls_clicked']:
        # Normalize the URL to remove any query parameters
        # This is because where URLs appear more than once, Mailchimp will
        # provide a row for each instance. Normalizing allows the clicks to be
        # aggregated.
        parsed_url = urlparse(detail['url'])
        normalised_url = parsed_url.netloc + parsed_url.path

        # Aggregate clicks for the same URL
        if normalised_url not in clicks:
            clicks[normalised_url] = detail['total_clicks']
        else:
            clicks[normalised_url] += detail['total_clicks']

        # Remove URLs with insufficient clicks
        if clicks[normalised_url] < minimum_clicks:
            del clicks[normalised_url]

    return clicks
