import os
import json
from flask import Flask, render_template, request, jsonify
from eu_api_monitor import EUAPIMonitor
from config import SPAIN_GEOGRAPHY, MUNICIPALITY_CONFIG

app = Flask(__name__)

# Instancia global del monitor
monitor = EUAPIMonitor()

@app.route('/')
def index():
    """Sirve la página web principal"""
    return render_template('index.html', municipality_name=MUNICIPALITY_CONFIG.get('name', 'tu municipio'))

@app.route('/api/geography', methods=['GET'])
def get_geography():
    """Devuelve la estructura geográfica de España"""
    return jsonify(SPAIN_GEOGRAPHY)

@app.route('/api/search', methods=['POST'])
def search_calls():
    """Busca convocatorias según el ámbito y término"""
    data = request.json
    scope = data.get('scope', 'national')
    term = data.get('term', 'España')

    if scope == 'national':
        search_term = "España"
    elif scope in ['regional', 'provincial', 'free']:
        search_term = term
    else:
        search_term = "España"

    try:
        # Buscar resultados
        results = monitor.search_opportunities(search_term)
        
        # Procesar y filtrar (only_new=False para mostrar todo lo activo)
        processed_calls = monitor.process_search_results(results, only_new=False)
        
        return jsonify({"success": True, "calls": processed_calls})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/notify', methods=['POST'])
def notify_call():
    """Envía notificación de una convocatoria específica"""
    call_data = request.json
    try:
        # Asumiendo que call_data contiene la estructura necesaria
        monitor.notification_service.send_notifications(call_data)
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

if __name__ == '__main__':
    # Ejecutar en modo debug para facilitar el desarrollo
    app.run(host='0.0.0.0', port=5000, debug=True)
