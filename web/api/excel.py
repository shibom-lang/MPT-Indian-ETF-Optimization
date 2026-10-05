from http.server import BaseHTTPRequestHandler
import os
import sys
from urllib.parse import urlparse, parse_qs

sys.path.append(os.path.dirname(__file__))

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            qs = parse_qs(urlparse(self.path).query)
            amount = float(qs.get('amount', ['100000'])[0])
            strategy = qs.get('strategy', ['maxsharpe'])[0]
            
            import excel_generator
            excel_path = excel_generator.generate_excel(amount, strategy)
            
            with open(excel_path, "rb") as f:
                excel_data = f.read()
                
            self.send_response(200)
            self.send_header('Content-type', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            self.send_header('Content-Disposition', f'attachment; filename="Portfolio_Wealth_Model_{strategy}.xlsx"')
            self.end_headers()
            self.wfile.write(excel_data)
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(f"Error generating excel: {str(e)}".encode('utf-8'))
        return
