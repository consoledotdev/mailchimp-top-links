# Mailchimp Top Links

Returns the top clicked links over the specified time period.

## Usage

```shell
Usage: mctl [OPTIONS]

  Exports top links from Mailchimp campaigns sent over the specified period to
  CSV.

Options:
  --api_key TEXT            Mailchimp API key  [required]
  --server TEXT             Mailchimp server
  --list_id TEXT            Mailchimp list ID  [required]
  --since TEXT              Examine campaigns since this date (yyyy-mm-dd)
                            [required]
  --before TEXT             Examine campaigns before this date (yyyy-mm-dd)
                            [required]
  --minimum_clicks INTEGER  Exclude links with fewer clicks than this
  --help                    Show this message and exit.
```

## Dev Setup

```shell
. venv/bin/activate
pip install --editable .
```