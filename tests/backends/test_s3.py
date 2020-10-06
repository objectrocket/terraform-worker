def test_s3_hcl(basec):
    render = basec.backend.hcl("test")
    expected_render = """terraform {
  backend "s3" {
    region = "us-west-2"
    bucket = "test_bucket"
    key = "terraform/test-0001/test/terraform.tfstate"
    dynamodb_table = "terraform-test-0001"
    encrypt = "true"
  }
}"""
    assert render == expected_render


def test_s3_data_hcl(basec):
    render = basec.backend.data_hcl("test2")
    expected_render = """data "terraform_remote_state" "test" {
  backend = "s3"
  config = {
    region = "us-west-2"
    bucket = "test_bucket"
    key = "terraform/test-0001/test/terraform.tfstate"
  }
}
"""
    assert render == expected_render
