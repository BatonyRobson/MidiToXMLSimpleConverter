import os
import sys

try:
    import mido
except ImportError:
    print("!!! Библиотека 'mido' не установлена. Запусти: pip install mido")
    input()
    sys.exit()

from xml.etree.ElementTree import Element, SubElement, ElementTree, indent

def midi_to_premiere_xml(midi_path, fps, bpm):
    try:
        mid = mido.MidiFile(midi_path)
        ticks_per_beat = mid.ticks_per_beat
        
        # Получаем только имя файла без расширения (строкой)
        pure_name = os.path.splitext(os.path.basename(midi_path))[0]
        
        # Корневой элемент с правильным заголовкум
        xmeml = Element('xmeml', version="1")
        sequence = SubElement(xmeml, 'sequence')
        SubElement(sequence, 'name').text = f"{pure_name}_MIDI"
        
        rate = SubElement(sequence, 'rate')
        SubElement(rate, 'timebase').text = str(fps)
        SubElement(rate, 'ntsc').text = "FALSE"
        
        media = SubElement(sequence, 'media')
        video = SubElement(media, 'video')
        # Создаем хотя бы одну пустую дорожку, иначе Premiere выдаст Generic Error
        track_element = SubElement(video, 'track')
        
        # Обработка нот
        marker_count = 0
        for track in mid.tracks:
            abs_ticks = 0
            for msg in track:
                abs_ticks += msg.time
                if msg.type == 'note_on' and msg.velocity > 0:
                    # Математика: (Тики / Разрешение) * (60 / BPM) * FPS
                    seconds = (abs_ticks / ticks_per_beat) * (60.0 / bpm)
                    frame = int(round(seconds * fps))
                    
                    marker = SubElement(sequence, 'marker')
                    SubElement(marker, 'name').text = f"Note {msg.note}"
                    SubElement(marker, 'in').text = str(frame)
                    SubElement(marker, 'out').text = str(frame)
                    marker_count += 1

        output_xml = f"{pure_name}_{fps}fps.xml"
        
        # Сохранение с принудительным заголовком DOCTYPE
        with open(output_xml, 'wb') as f:
            f.write(b'<?xml version="1.0" encoding="UTF-8"?>\n')
            f.write(b'<!DOCTYPE xmeml>\n')
            tree = ElementTree(xmeml)
            indent(tree, space="  ", level=0)
            tree.write(f, encoding="UTF-8", xml_declaration=False)
            
        print(f"[+] ГОТОВО: {output_xml} | Маркеров: {marker_count}")
        
    except Exception as e:
        print(f"[!] Ошибка в файле {midi_path}: {e}")

def main():
    # Переход в папку со скриптом
    script_dir = os.path.dirname(os.path.abspath(__file__))
    if script_dir:
        os.chdir(script_dir)
    
    files = [f for f in os.listdir('.') if f.lower().endswith(('.mid', '.midi'))]
    
    if not files:
        print(f"\n[!] MIDI-файлы не найдены в {os.getcwd()}")
    else:
        print(f"\nНайдено MIDI: {len(files)}")
        try:
            fps_val = input("Введите FPS (например 60): ")
            bpm_val = input("Введите BPM (например 173): ")
            
            fps = int(fps_val) if fps_val else 60
            bpm = float(bpm_val) if bpm_val else 120.0
            
            for f in files:
                midi_to_premiere_xml(f, fps, bpm)
                
        except ValueError:
            print("Ошибка: Вводи только числа.")

    print("\n---")
    input("Нажми Enter для выхода...")

if __name__ == "__main__":
    main()
