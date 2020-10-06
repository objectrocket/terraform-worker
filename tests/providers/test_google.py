def test_google_hcl(basec):
    render = basec.providers["google"].hcl()
    expected_render = """provider "google" {
  region = "us-west-2"
  credentials = file("/home/test/test-creds.json")
}"""

    assert render == expected_render
