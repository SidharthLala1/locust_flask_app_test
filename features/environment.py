from behave.model import Status
import datetime

def before_all(context):
    context.start_time = datetime.datetime.now()

def after_all(context):
    context.end_time = datetime.datetime.now()
    context.duration = context.end_time - context.start_time

def before_feature(context, feature):
    feature.start_time = datetime.datetime.now()

def after_feature(context, feature):
    feature.end_time = datetime.datetime.now()
    feature.duration = feature.end_time - feature.start_time

def before_scenario(context, scenario):
    scenario.start_time = datetime.datetime.now()

def after_scenario(context, scenario):
    scenario.end_time = datetime.datetime.now()
    scenario.duration = scenario.end_time - scenario.start_time