from flask import Blueprint, render_template, redirect, url_for, session, flash, jsonify
from models.medicamentos import Medicamentos  
from datetime import datetime

medicamentos_bp = Blueprint('medicamentos', __name__)

@medicamentos_bp.route('/paciente/medicamentos')
def listar_medicamentos():
    # Obtener medicamentos usando el Modelo
    medicamentos = Medicamentos.obtener_medicamentos_por_usuario(session['user_id'])
    
    if medicamentos is None:
        return render_template('paciente/medicamentos.html', medicamentos=[])
    
    return render_template('paciente/medicamentos.html', medicamentos=medicamentos)

@medicamentos_bp.route('/api/medicamentos/proximos')
def proximos_medicamentos():
    if 'user_id' not in session:
        return jsonify({'error': 'No autorizado'}), 401
    
    # Obtener medicamentos del usuario
    medicamentos = Medicamentos.obtener_medicamentos_por_usuario(session['user_id'])
    if medicamentos is None:
        return jsonify([])
    
    # Filtrar medicamentos próximos
    now = datetime.now()
    now_minutes = now.hour * 60 + now.minute
    resultados = []
    
    for med in medicamentos:
        # Verificar cada horario del medicamento
        horarios = []
        if med.get('horario_dia'):
            h, m = map(int, med['horario_dia'].split(':'))
            horarios.append(h * 60 + m)
        if med.get('horario_tarde'):
            h, m = map(int, med['horario_tarde'].split(':'))
            horarios.append(h * 60 + m)
        if med.get('horario_noche'):
            h, m = map(int, med['horario_noche'].split(':'))
            horarios.append(h * 60 + m)
        
        # Verificar si algún horario está dentro del rango
        for horario in horarios:
            if 0 <= (horario - now_minutes) <= 30:  # Próximos 30 minutos
                resultados.append({
                    'id': med['idmedicamentos'],
                    'medicamento': med['medicamento'],
                    'dosis': med['dosis'],
                    'horario_dia': med.get('horario_dia'),
                    'horario_tarde': med.get('horario_tarde'),
                    'horario_noche': med.get('horario_noche')
                })
                break
    
    return jsonify(resultados)