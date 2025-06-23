# content_generation_agent/__init__.py
"""
Exposes the root agent of the application to the ADK framework.

The ADK server looks for a 'root_agent' in this file to start the execution.
"""
from .pipeline import root_agent