
# test_log_integrity.py
def test_log_output():
    run_processing()
    with open("watermark.log") as f:
        assert "Processed" in f.read()