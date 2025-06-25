from flask import Blueprint, request, flash, redirect, url_for, render_template, session
from models.triaje import Dato
from datetime import datetime, timedelta
import pytz

biometrico_bp = Blueprint('triaje', __name__)

@biometrico_bp.route('/paciente/datos-biometricos', methods=['GET', 'POST'])
def datos_biometricos():
    if 'user_id' not in session or session.get('user_rol') != 'paciente':
        flash('Debes iniciar sesión como paciente para acceder a esta página', 'danger')
        return redirect(url_for('triaje.datos_biometricos'))
    
    if request.method == 'POST':
        try:
            glucosa = request.form.get('glucosa')
            presion_sistolica = request.form.get('presion_sistolica')
            presion_diastolica = request.form.get('presion_diastolica')
            frecuencia_cardiaca = request.form.get('frecuencia_cardiaca')
            notas = request.form.get('notas', '').strip()

            glucosa = int(glucosa)
            presion_sistolica = int(presion_sistolica)
            presion_diastolica = int(presion_diastolica)
            frecuencia_cardiaca = int(frecuencia_cardiaca)
            
            if presion_sistolica <= presion_diastolica:
                flash('La presión sistólica debe ser mayor que la diastólica', 'warning')
                return render_template('paciente/datos_biometricos.html')
            
            resultado = Dato.insertar_dato(
                glucosa=glucosa,
                sistolica=presion_sistolica,
                diastolica=presion_diastolica,
                frecuencia_cardiaca=frecuencia_cardiaca,
                descripcion=notas,
                usuarios_id=session['user_id']
            )
            
            if resultado:
                return redirect(url_for('triaje.datos_biometricos'))
            else:
                flash('Error al guardar los datos. Por favor intenta nuevamente.', 'danger')
                
        except ValueError as e:
            flash('Por favor ingresa valores numéricos válidos', 'warning')
        except Exception as e:
            flash(f'Error inesperado: {str(e)}', 'danger')
    
    return render_template('paciente/datos_biometricos.html')