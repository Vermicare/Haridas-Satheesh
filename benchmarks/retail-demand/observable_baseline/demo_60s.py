"""Public-safe <60-second demo; synthetic data only. No dataset downloaded."""
import datetime as dt
import json
import tempfile
from pathlib import Path
from retail_gate import benchmark

with tempfile.TemporaryDirectory() as folder:
    fixture = Path(folder) / 'fictional.jsonl'
    with fixture.open('w', encoding='utf-8') as stream:
        for i in range(84):
            status = [0] * 24
            if i % 5 == 0:
                status[11] = 1
            sales = [0.0] * 24
            sales[8] = float(1 + i % 7)
            row = {'store_id': 1, 'product_id': 2,
                   'dt': (dt.date(2024, 1, 1) + dt.timedelta(days=i)).isoformat(),
                   'hours_sale': sales, 'hours_stock_status': status,
                   'stock_hour6_22_cnt': sum(status[6:22])}
            stream.write(json.dumps(row, sort_keys=True) + '\n')
    report = benchmark(fixture, synthetic=True)
    print('FICTIONAL ONLY | external dataset: NOT DOWNLOADED')
    print('Input SHA-256:', report['input_sha256'])
    for fold in report['folds']:
        scores = {name: value['mae_uncensored_only'] for name, value in fold['models'].items()}
        print(fold['origin_date'], 'eligible:', fold['uncensored_test_days'], 'MAE:', scores)
    print('Latent demand truth, business uplift, and public-data results: TBD')
