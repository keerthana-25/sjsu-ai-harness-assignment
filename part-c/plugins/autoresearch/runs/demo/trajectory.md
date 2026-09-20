# AutoResearch trajectory — tasks/digits_classifier

Model: `nvidia/nemotron-3-super-120b-a12b:free`  
Iterations: 5  
Best metric: **0.9806**

| Iteration | Status | Metric | Note |
|---|---|---|---|
| 0 | kept | 0.4250 | baseline |
| 1 | kept | 0.9667 | kept: 0.4250 -> 0.9667 (+0.5417) |
| 2 | reverted | FAILED | reverted: LLM call failed (empty response from model 'nvidia/nemotron-3-super-120b-a12b:free': ChatCompletion(id='gen-1789864459-MWopRke8EAYfUP7veir4', choices=None, created=None, model=None, object=None, service_tier=None, system_fingerprint=None, usage=None, error={'message': 'Upstream error from Nvidia: Service temporarily overloaded', 'code': 503, 'metadata': {'error_type': 'provider_overloaded'}})) |
| 3 | kept | 0.9722 | kept: 0.9667 -> 0.9722 (+0.0056) |
| 4 | kept | 0.9806 | kept: 0.9722 -> 0.9806 (+0.0083) |
| 5 | reverted | 0.9806 | reverted: 0.9806 <= best 0.9806 |
