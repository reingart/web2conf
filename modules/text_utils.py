#!/usr/bin/env python
# coding: utf8

def cram(text, maxlen):
    """Omit part of a string if needed to make it fit in a
       maximum length."""
    text = text.decode('utf-8')
    if len(text) > maxlen:
        pre = max(0, (maxlen-3))
        text = text[:pre] + '...'
    return text.encode('utf8')
