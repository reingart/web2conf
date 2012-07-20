# coding: utf8

def index(): return plugin_flatpage()

@auth.requires_login()
def books(): return plugin_flatpage()

@auth.requires_login()
def tools(): return plugin_flatpage()

@auth.requires_login()
def other(): return plugin_flatpage()
