# Mailchimp Top Links

Returns the top clicked links over the specified time period.

## Usage

```bash
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
python3 -m venv .venv
source .venv/bin/activate
pip install --editable .
```

## Run

```bash
mctl \
  --api_key $(op read "op://Home/Mailchimp API Key/credential") \
  --server us7 \
  --list_id 267911a165 \
  --since 2024-01-01 \
  --before 2024-12-23
```