import csv
import math
import tempfile
import unittest
from pathlib import Path
from scripts.build_historical_cycle_timeline import build, markdown

class TimelineTests(unittest.TestCase):
    def test_complete_history(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            folder=root/"data/industry_observations"
            folder.mkdir(parents=True)
            for name in ("UNRATE","CPIAUCSL","INDPRO","TOTALSL","BUSLOANS"):
                with (folder/(name+"_monthly.csv")).open("w",newline="") as f:
                    writer=csv.DictWriter(f,fieldnames=["date","value"])
                    writer.writeheader()
                    for i in range(40):
                        year,month=2010+i//12,i%12+1
                        value=5.0 if name=="UNRATE" else round(100*math.exp(i*.01),5)
                        writer.writerow({"date":f"{year:04d}-{month:02d}-01","value":value})
            report=build(root)
            self.assertEqual(report["months"],28)
            self.assertEqual(report["first_month"],"2011-01")
            self.assertIn("Condition prevalence",markdown(report))
            self.assertFalse(report["point_in_time_certified"])

if __name__=="__main__":
    unittest.main()
