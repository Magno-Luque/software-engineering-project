from flask import Blueprint, render_template, redirect, url_for, session, flash, request
from models.alertacriticaParamedico import Alerta
from datetime import datetime

paramedico_bp = Blueprint('paramedico', __name__)

@paramedico_bp.route('/paramedico/alertas_criticas', methods=['GET', 'POST'])
def alertas():
    paramedico_id = 1
    
    if request.method == 'POST':
        alerta_id = request.form.get('alerta_id')
        accion = request.form.get('accion')
        nota = request.form.get('nota', None)
        
        if not alerta_id or not accion:
            flash('Datos incompletos', 'error')
            return redirect(url_for('paramedico.alertas'))
        
        if accion == 'emergencia':
            estado = 'Emergencia'
        elif accion == 'resolver':
            estado = 'Controlada'
        else:
            flash('Acción no válida', 'error')
            return redirect(url_for('paramedico.alertas'))
        
        if Alerta.actualizar_estado_alerta(alerta_id, estado, paramedico_id, nota):
            flash(f'Alerta marcada como {estado.lower()}', 'success')
        else:
            flash('Error al actualizar la alerta', 'error')
        
        return redirect(url_for('paramedico.alertas'))
    
    # GET request
    alertas = Alerta.obtener_alertas_para_paramedico()
    return render_template('paramedico/alertas_criticas.html', alertas=alertas)

@paramedico_bp.route('/paramedico/agregar_nota_alerta', methods=['POST'])
def agregar_nota_alerta():
    alerta_id = request.form.get('alerta_id')
    nota = request.form.get('nota')
    paramedico_id = session.get('user_id')
    
    if Alerta.actualizar_estado_alerta(alerta_id, 'nota_agregada', nota=nota, paramedico_id=paramedico_id):
        flash('Nota agregada correctamente', 'success')
    else:
        flash('Error al agregar la nota', 'error')
    
    return redirect(url_for('paramedico.agregar_nota_alerta'))