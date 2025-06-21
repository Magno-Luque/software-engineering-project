-- SCRIPT SQL SIMPLE - SOLO EJECUTAR ESTO EN TU BASE DE DATOS

-- 1. Modificar el campo estado para incluir OCUPADO
ALTER TABLE horarios_disponibles 
MODIFY COLUMN estado ENUM('ACTIVO', 'INACTIVO', 'BLOQUEADO', 'OCUPADO') DEFAULT 'ACTIVO';

-- 2. Trigger simple para marcar slot como ocupado cuando se crea una cita
DELIMITER //

CREATE TRIGGER tr_marcar_slot_ocupado
AFTER INSERT ON citas
FOR EACH ROW
BEGIN
    UPDATE horarios_disponibles 
    SET estado = 'OCUPADO' 
    WHERE id = NEW.horario_id;
END//

-- 3. Trigger simple para liberar slot cuando se cancela/elimina una cita
CREATE TRIGGER tr_liberar_slot_cita_cancelada
AFTER UPDATE ON citas
FOR EACH ROW
BEGIN
    IF NEW.estado = 'CANCELADA' AND OLD.estado != 'CANCELADA' THEN
        UPDATE horarios_disponibles 
        SET estado = 'ACTIVO' 
        WHERE id = NEW.horario_id;
    END IF;
END//

CREATE TRIGGER tr_liberar_slot_cita_eliminada
AFTER DELETE ON citas
FOR EACH ROW
BEGIN
    UPDATE horarios_disponibles 
    SET estado = 'ACTIVO' 
    WHERE id = OLD.horario_id;
END//

DELIMITER ;