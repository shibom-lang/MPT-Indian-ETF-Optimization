from http.server import BaseHTTPRequestHandler
import os

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            # Check public directory first, then fallback to current directory or /tmp
            candidates = [
                os.path.join(os.path.dirname(__file__), "../public/MPT_Indian_ETF_Detailed_Report.pdf"),
                os.path.join(os.path.dirname(__file__), "MPT_Indian_ETF_Detailed_Report.pdf"),
                "/tmp/MPT_Indian_ETF_Detailed_Report.pdf"
            ]
            pdf_path = None
            for p in candidates:
                if os.path.exists(p):
                    pdf_path = p
                    break
            
            if not pdf_path:
                raise FileNotFoundError("Report PDF not found in repository assets.")
                
            with open(pdf_path, "rb") as f:
                pdf_data = f.read()
                
            self.send_response(200)
            self.send_header('Content-type', 'application/pdf')
            self.send_header('Content-Disposition', 'attachment; filename="MPT_Indian_ETF_Detailed_Report.pdf"')
            self.end_headers()
            self.wfile.write(pdf_data)
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(f"Error serving report: {str(e)}".encode('utf-8'))
        return
