from http.server import BaseHTTPRequestHandler
import os
import sys

# Ensure api folder is in path for absolute imports if needed
sys.path.append(os.path.dirname(__file__))

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            # Import and run the generator
            import mpt_generator
            mpt_generator.generate_report()
            
            pdf_path = "/tmp/MPT_Indian_ETF_Detailed_Report.pdf"
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
            self.wfile.write(f"Error generating report: {str(e)}".encode('utf-8'))
        return
