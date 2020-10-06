def test_aws_hcl(basec):
    render = basec.providers["aws"].hcl()
    expected_render = """provider "aws" {
  region = "us-west-2"
}"""
    assert render == expected_render
