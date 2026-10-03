"""Local browser-test fixture. Every provider is mocked; never use for deployment.

Run explicitly with: python -m backend.tests.browser_server
Only fake key `trace-ui-test-key` should be entered in the local settings drawer.
"""
import json
import re
from types import SimpleNamespace as NS
import uvicorn
from backend.app import app
from backend import engine
from backend.events import emit
from workflows import research_agent,code_copilot,document_intelligence

REPORT='# Mock-provider browser test\n\n'+ '\n\n'.join(f'## Finding {i+1}\n\n'+('The fictional pilot has a defined scope, an explicit escalation path, and evidence available for inspection. '*8)+'[S1]' for i in range(35))

def completion(**kwargs):
    system=kwargs['messages'][0]['content'];user=kwargs['messages'][-1]['content']
    if 'research plans' in system: value={'goal':'Browser test','sub_questions':['What is supported?'],'report_sections':['Findings']}
    elif 'summarize research sources' in system:
        label=re.search(r'Source label: (S\d+)',user).group(1)
        value={'label':label,'title':'Mock source','summary':'Fictional pilot notes for a browser integration check.','key_points':['Bounded scope'],'relevance':'Test fixture'}
    elif 'quality reviewer' in system: value={'passes_review':True,'issues':[],'revised_report':REPORT}
    elif 'Return only the requested code' in system: value='def broken(:'
    elif 'You fix code' in system: value='def categories(items):\n    return list(dict.fromkeys(items))\n\n# '+('wide_code_block_'*80)
    elif 'analyze business' in system:value='invalid JSON to exercise preserved heuristics'
    else:value=REPORT
    return NS(choices=[NS(message=NS(content=json.dumps(value) if isinstance(value,dict) else value))])
client=NS(chat=NS(completions=NS(create=completion)))
for module in [research_agent,code_copilot,document_intelligence]:module.OpenAI=lambda **kwargs:client
class Article:
    title='Mock-provider source';text='Fictional repair pilot. Ordinary fixes use appointments. Specialist issues need human review. '
    def __init__(self,url):self.url=url
    def download(self):
        if self.url.endswith('/bad'):raise ValueError('Synthetic source extraction failure')
    def parse(self):pass
research_agent.Article=Article
execute=engine.execute
def mocked_execute(*args,**kwargs):
    if args[3]!='trace-ui-test-key' or args[2].tool not in {'research','code','documents'}:
        raise ValueError('This fixture accepts only its fake key and Research, Code or Document tests.')
    emit('warning',message='Mock-provider browser check — no live AI request.')
    return execute(*args,**kwargs)
engine.execute=mocked_execute
if __name__=='__main__':uvicorn.run(app,host='0.0.0.0',port=8000,access_log=False)
