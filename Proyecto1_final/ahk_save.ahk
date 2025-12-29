#Persistent
#SingleInstance force

; Script de AutoHotkey para guardar con Ctrl+S
Loop {
    ; Esperar comandos de Python
    FileRead, comando, ahk_save_command.txt
    if (ErrorLevel = 0) {
        FileDelete, ahk_save_command.txt
        
        ; Parsear comando: acción
        accion := Trim(comando)
        
        ; Ejecutar acción de guardar
        if (accion = "SAVE") {
            ; Enviar Ctrl+S para guardar
            Send, ^s
            Sleep, 500
            
            ; Confirmación para Python
            FileAppend, saved, ahk_save_done.txt
            Sleep, 100
            FileDelete, ahk_save_done.txt
        }
    }
    Sleep, 500  ; Revisar cada medio segundo
}