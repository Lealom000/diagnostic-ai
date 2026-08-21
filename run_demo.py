from app import Handler, ThreadingHTTPServer
import os
if __name__ == '__main__':
    port=int(os.getenv('PORT','8000')); print(f'Open http://localhost:{port}')
    ThreadingHTTPServer(('0.0.0.0',port),Handler).serve_forever()
