import tiktoken
from models import Emails
from services.textprocessing import EmailTextProcessor


def test_textprocessor_none_none_should_work_with_only_body():
    processor = EmailTextProcessor(truncate_method="none")
    emails: Emails = {"sender": [None], "subject": [None], "body": ["hello world"]}
    results = processor.to_text(emails)
    assert len(results) == 1
    assert "hello world" in results[0]


def test_textprocessor_none_none_should_include_sender_and_subject_if_provided():
    processor = EmailTextProcessor(truncate_method="none")
    emails: Emails = {
        "sender": ["mail <yo@gmail.com>"],
        "subject": ["WARNING"],
        "body": ["hello world"],
    }
    results = processor.to_text(emails)
    assert len(results) == 1
    assert "mail <yo@gmail.com>" in results[0]
    assert "WARNING" in results[0]
    assert "hello world" in results[0]


def test_textprocessor_none_none_should_include_label_if_provided():
    processor = EmailTextProcessor(truncate_method="none")
    emails: Emails = {
        "sender": [None, None],
        "subject": [None, None],
        "body": ["hello world", "bye"],
        "label": [1.0, 0.0],
    }
    results = processor.to_text(emails)
    assert len(results) == 2
    assert "hello world" in results[0]
    assert "phishing" in results[0]
    assert "bye" in results[1]
    assert "benign" in results[1]


def test_textprocessor_end_none_should_truncate_from_end_to_around_max_tokens():
    processor = EmailTextProcessor(
        max_tokens=16, truncate_method="end", tokenizer_model=None
    )
    processor.tokens_per_chr = 0.5
    emails: Emails = {
        "sender": ["one two three four"],
        "subject": ["five six seven eight"],
        "body": ["nine ten eleven twelve"],
        "label": [0.9],
    }
    results = processor.to_text(emails)
    assert len(results) == 1
    assert len(results[0]) == 32  # 16 tokens if 0.5 tokens/char
    assert "phishing" in results[0]
    assert "twelve" not in results[0]  # truncated


def test_textprocessor_end_model_should_truncate_from_end_to_exactly_max_tokens():
    tokenizer = tiktoken.encoding_for_model("gpt-4o")
    processor = EmailTextProcessor(
        max_tokens=16, truncate_method="end", tokenizer_model="gpt-4o"
    )
    emails: Emails = {
        "sender": ["one two three four"],
        "subject": ["five six seven eight"],
        "body": ["nine ten eleven twelve"],
        "label": [0.9],
    }
    results = processor.to_text(emails)
    assert len(results) == 1
    assert len(tokenizer.encode(results[0])) == 16
    assert "phishing" in results[0]
    assert "twelve" not in results[0]  # truncated


def test_textprocessor_content_none_should_always_include_body():
    processor = EmailTextProcessor(
        max_tokens=1, truncate_method="content", tokenizer_model=None
    )
    processor.tokens_per_chr = 0.5
    emails: Emails = {
        "sender": ["one two three four"],
        "subject": ["five six seven eight"],
        "body": ["nine ten eleven twelve"],
    }
    results = processor.to_text(emails)
    assert len(results) == 1
    assert "nine ten eleven twelve" in results[0]


def test_textprocessor_content_model_should_always_include_body():
    processor = EmailTextProcessor(
        max_tokens=1, truncate_method="content", tokenizer_model="gpt-4o"
    )
    emails: Emails = {
        "sender": ["one two three four"],
        "subject": ["five six seven eight"],
        "body": ["nine ten eleven twelve"],
    }
    results = processor.to_text(emails)
    assert len(results) == 1
    assert "nine ten eleven twelve" in results[0]


def test_textprocessor_content_none_should_include_everything_if_they_fit():
    processor = EmailTextProcessor(
        max_tokens=1024, truncate_method="content", tokenizer_model=None
    )
    processor.tokens_per_chr = 0.5
    emails: Emails = {
        "sender": ["one two three four"],
        "subject": ["five six seven eight"],
        "body": ["nine ten eleven twelve"],
        "label": [0.6],
    }
    results = processor.to_text(emails)
    assert len(results) == 1
    assert "one two three four" in results[0]
    assert "five six seven eight" in results[0]
    assert "nine ten eleven twelve" in results[0]
    assert "phishing" in results[0]


def test_textprocessor_content_model_should_include_everything_if_they_fit():
    processor = EmailTextProcessor(
        max_tokens=1024, truncate_method="content", tokenizer_model="gpt-4o"
    )
    emails: Emails = {
        "sender": ["one two three four"],
        "subject": ["five six seven eight"],
        "body": ["nine ten eleven twelve"],
        "label": [0.6],
    }
    results = processor.to_text(emails)
    assert len(results) == 1
    assert "one two three four" in results[0]
    assert "five six seven eight" in results[0]
    assert "nine ten eleven twelve" in results[0]
    assert "phishing" in results[0]


def test_textprocessor_content_none_should_include_label_sender_then_subject():
    added = set()
    for max_tokens in range(64):
        processor = EmailTextProcessor(
            max_tokens, truncate_method="content", tokenizer_model=None
        )
        processor.tokens_per_chr = 0.5
        emails: Emails = {
            "sender": ["AB"],
            "subject": ["XY"],
            "body": ["body"],
            "label": [0.6],
        }
        results = processor.to_text(emails)
        if "label" not in added and "phishing" in results[0]:
            assert len(added) == 0
            added.add("label")
        if "sender" not in added and "AB" in results[0]:
            assert len(added) == 1
            added.add("sender")
        if "subject" not in added and "XY" in results[0]:
            assert len(added) == 2
            added.add("subject")
        if len(added) == 3:
            break


def test_textprocessor_content_model_should_include_label_sender_then_subject():
    # slowly increase max tokens and see which parts get added first
    added = set()
    for max_tokens in range(64):
        processor = EmailTextProcessor(
            max_tokens, truncate_method="content", tokenizer_model="gpt-4o"
        )
        emails: Emails = {
            "sender": ["AB"],
            "subject": ["XY"],
            "body": ["body"],
            "label": [0.6],
        }
        results = processor.to_text(emails)
        if "label" not in added and "phishing" in results[0]:
            assert len(added) == 0
            added.add("label")
        if "sender" not in added and "AB" in results[0]:
            assert len(added) == 1
            added.add("sender")
        if "subject" not in added and "XY" in results[0]:
            assert len(added) == 2
            added.add("subject")
        if len(added) == 3:
            break


def test_textprocessor_contentend_none_should_truncate_from_end_to_around_max_tokens():
    processor = EmailTextProcessor(
        max_tokens=16, truncate_method="content-end", tokenizer_model=None
    )
    processor.tokens_per_chr = 0.5
    emails: Emails = {
        "sender": ["one two three four"],
        "subject": ["five six seven eight"],
        "body": ["nine ten eleven twelve"],
        "label": [0.1],
    }
    results = processor.to_text(emails)
    assert len(results) == 1
    assert len(results[0]) == 32  # 16 tokens if 0.5 tokens/char
    assert "benign" in results[0]
    assert "twelve" not in results[0]  # truncated


def test_textprocessor_contentend_model_should_truncate_from_end_to_exactly_max_tokens():
    tokenizer = tiktoken.encoding_for_model("gpt-4o")
    processor = EmailTextProcessor(
        max_tokens=16, truncate_method="content-end", tokenizer_model="gpt-4o"
    )
    emails: Emails = {
        "sender": ["one two three four"],
        "subject": ["five six seven eight"],
        "body": ["nine ten eleven twelve"],
        "label": [0.1],
    }
    results = processor.to_text(emails)
    assert len(results) == 1
    assert len(tokenizer.encode(results[0])) == 16
    assert "benign" in results[0]
    assert "twelve" not in results[0]  # truncated


def test_textprocessor_contentend_none_should_include_everything_if_they_fit():
    processor = EmailTextProcessor(
        max_tokens=1024, truncate_method="content-end", tokenizer_model=None
    )
    processor.tokens_per_chr = 0.5
    emails: Emails = {
        "sender": ["one two three four"],
        "subject": ["five six seven eight"],
        "body": ["nine ten eleven twelve"],
        "label": [0.2],
    }
    results = processor.to_text(emails)
    assert len(results) == 1
    assert "one two three four" in results[0]
    assert "five six seven eight" in results[0]
    assert "nine ten eleven twelve" in results[0]
    assert "benign" in results[0]


def test_textprocessor_contentend_model_should_include_everything_if_they_fit():
    processor = EmailTextProcessor(
        max_tokens=1024, truncate_method="content-end", tokenizer_model="gpt-4o"
    )
    emails: Emails = {
        "sender": ["one two three four"],
        "subject": ["five six seven eight"],
        "body": ["nine ten eleven twelve"],
        "label": [0.2],
    }
    results = processor.to_text(emails)
    assert len(results) == 1
    assert "one two three four" in results[0]
    assert "five six seven eight" in results[0]
    assert "nine ten eleven twelve" in results[0]
    assert "benign" in results[0]


def test_textprocessor_contentend_none_should_include_label_sender_then_subject():
    added = set()
    for max_tokens in range(64):
        processor = EmailTextProcessor(
            max_tokens, truncate_method="content-end", tokenizer_model=None
        )
        processor.tokens_per_chr = 0.5
        emails: Emails = {
            "sender": ["AB"],
            "subject": ["XY"],
            "body": ["body"],
            "label": [0.6],
        }
        results = processor.to_text(emails)
        if "label" not in added and "phishing" in results[0]:
            assert len(added) == 0
            added.add("label")
        if "sender" not in added and "AB" in results[0]:
            assert len(added) == 1
            added.add("sender")
        if "subject" not in added and "XY" in results[0]:
            assert len(added) == 2
            added.add("subject")
        if len(added) == 3:
            break


def test_textprocessor_contentend_model_should_include_label_sender_then_subject():
    added = set()
    for max_tokens in range(64):
        processor = EmailTextProcessor(
            max_tokens, truncate_method="content-end", tokenizer_model="gpt-4o"
        )
        emails: Emails = {
            "sender": ["AB"],
            "subject": ["XY"],
            "body": ["body"],
            "label": [0.6],
        }
        results = processor.to_text(emails)
        if "label" not in added and "phishing" in results[0]:
            assert len(added) == 0
            added.add("label")
        if "sender" not in added and "AB" in results[0]:
            assert len(added) == 1
            added.add("sender")
        if "subject" not in added and "XY" in results[0]:
            assert len(added) == 2
            added.add("subject")
        if len(added) == 3:
            break
