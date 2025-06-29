from flask import Blueprint, request, flash, redirect, url_for, render_template, session
from models.infoadicional import InfoAdicional
from datetime import datetime, timedelta
import pytz

infoadicional_bp = Blueprint('infoadicional', __name__)

@infoadicional_bp.route('/paciente/actividad-fisica', methods=['GET', 'POST'])
def informacion_adicional():
    if request.method == 'POST':
        try:
            desayuno_comida = request.form.get('desayuno_comida', '').strip()
            desayuno_porcion = request.form.get('desayuno_porcion', '').strip()
            desayuno_notas = request.form.get('desayuno_notas', '').strip()
            almuerzo_comida = request.form.get('almuerzo_comida', '').strip()
            almuerzo_porcion = request.form.get('almuerzo_porcion', '').strip()
            almuerzo_notas = request.form.get('almuerzo_notas', '').strip()
            cena_comida = request.form.get('cena_comida', '').strip()
            cena_porcion = request.form.get('cena_porcion', '').strip()
            cena_notas = request.form.get('cena_notas', '').strip()
            tipo_actividad = request.form.get('tipo_actividad', '').strip()
            intensidad = request.form.get('intensidad', '').strip()
            tiempo = request.form.get('tiempo')
            notas_actividad = request.form.get('notas_actividad')
            
            resultado = InfoAdicional.insertar_dato(
                desayuno_comida=desayuno_comida, 
                desayuno_porcion=desayuno_porcion, 
                desayuno_notas=desayuno_notas, 
                almuerzo_comida=almuerzo_comida, 
                almuerzo_porcion=almuerzo_porcion, 
                almuerzo_notas=almuerzo_notas, 
                cena_comida=cena_comida, 
                cena_porcion=cena_porcion, 
                cena_notas=cena_notas, 
                actividad=tipo_actividad, 
                intensidad=intensidad, 
                tiempo=tiempo, 
                notas_adicionales=notas_actividad,
                usuarios_id=session['user_id']
            )
            
            if resultado:
                flash('Actividad Fisica y Dieta registrada exitosamente', 'success')
                return redirect(url_for('paciente_actividad_fisica.paciente_actividad_fisica'))
                
        except ValueError as e:
            flash('Por favor ingresa valores numéricos válidos', 'warning')
        except Exception as e:
            flash(f'Error inesperado: {str(e)}', 'danger')
    
    return render_template('paciente/actividad_fisica.html')