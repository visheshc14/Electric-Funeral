#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from datetime import datetime

from flask import Flask
app = Flask(__name__)

@app.route("/")
def index():
    return f"<h1>Hello There Made By Vishesh<h1><h2>Last retrieved from server: {datetime.now().strftime('%F %T')}</h2>"
