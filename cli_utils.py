import click

import tokenizers

# Validator meant to be used as a callback in a Click argument or option.
def validate_tokenizer(ctx, param, value: str) -> tokenizers.Tokenizer:
    try:
        tokenizer_cls = getattr(tokenizers, value)
    except AttributeError:
        raise click.BadParameter(f"No tokenizer named {value} in {tokenizers}")
    else:
        return tokenizer_cls()
