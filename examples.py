"""
EJEMPLOS DE USO AVANZADO
Casos de uso reales para el Monitor de Convocatorias
"""

from eu_api_monitor import EUAPIMonitor
from notification_service import NotificationService
import json


# ============================================================================
# EJEMPLO 1: Búsqueda personalizada por términos específicos
# ============================================================================
def ejemplo_busqueda_personalizada():
    """Busca solo convocatorias de desarrollo rural en Castilla-La Mancha"""
    print("\n" + "=" * 60)
    print("EJEMPLO 1: Búsqueda personalizada")
    print("=" * 60)

    monitor = EUAPIMonitor()

    # Búscar un término específico
    results = monitor.search_opportunities("Castilla-La Mancha desarrollo rural")

    print(f"Encontradas {len(results)} convocatorias")
    for result in results[:3]:
        print(f"\n📢 {result.get('title', 'N/A')[:80]}")
        print(f"   URL: {result.get('url', 'N/A')[:60]}")


# ============================================================================
# EJEMPLO 2: Procesar convocatorias y filtrarlas manualmente
# ============================================================================
def ejemplo_procesamiento_manual():
    """Procesa convocatorias y aplica filtros personalizados"""
    print("\n" + "=" * 60)
    print("EJEMPLO 2: Procesamiento manual de convocatorias")
    print("=" * 60)

    monitor = EUAPIMonitor()

    # Obtener resultados
    results = monitor.search_opportunities("NextGenerationEU")

    # Filtro personalizado: solo convocatorias con palabras clave específicas
    filtros = {
        "presupuesto_minimo": "100000",
        "palabras_clave": ["municipios", "rural", "despoblación"],
    }

    convocatorias_filtradas = []
    for call in results:
        title = (call.get("title", "") or "").lower()
        description = (call.get("description", "") or "").lower()
        texto_completo = f"{title} {description}"

        # Verificar palabras clave
        tiene_palabras = any(
            palabra in texto_completo for palabra in filtros["palabras_clave"]
        )

        if tiene_palabras:
            convocatorias_filtradas.append(call)

    print(f"Resultados originales: {len(results)}")
    print(f"Después de filtrar: {len(convocatorias_filtradas)}")

    for call in convocatorias_filtradas[:2]:
        print(f"\n✅ {call.get('title', 'N/A')[:80]}")


# ============================================================================
# EJEMPLO 3: Exportar resultados a CSV
# ============================================================================
def ejemplo_exportar_csv():
    """Busca y exporta resultados a CSV para análisis posterior"""
    print("\n" + "=" * 60)
    print("EJEMPLO 3: Exportar a CSV")
    print("=" * 60)

    import csv
    from datetime import datetime

    monitor = EUAPIMonitor()
    results = monitor.search_opportunities("Despoblación")

    # Preparar datos para CSV
    filename = f"convocatorias_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Título", "URL", "Descripción", "Fuente"])

        for call in results[:10]:
            writer.writerow(
                [
                    call.get("title", ""),
                    call.get("url", ""),
                    (call.get("description", "") or "")[:100],
                    call.get("source", ""),
                ]
            )

    print(f"✅ Exportadas {len(results[:10])} convocatorias a: {filename}")


# ============================================================================
# EJEMPLO 4: Enviar notificación personalizada
# ============================================================================
def ejemplo_notificacion_personalizada():
    """Crea y envía una notificación personalizada"""
    print("\n" + "=" * 60)
    print("EJEMPLO 4: Notificación personalizada")
    print("=" * 60)

    service = NotificationService()

    # Crear convocatoria personalizada
    convocatoria_ejemplo = {
        "title": "Fondo de Dinamización de Municipios Rurales 2024",
        "budget": "€ 150.000 - € 500.000",
        "deadline": "30/06/2024",
        "summary": "Programa de apoyo a inversiones estratégicas en municipios con menos de 5.000 habitantes para diversificación económica y empleo.",
        "url": "https://data.europa.eu/ejemplo",
    }

    print("Envío de notificación personalizada:")
    # success = service.send_to_alcalde_and_secretario(convocatoria_ejemplo)
    # if success:
    print("✅ Notificación enviada exitosamente")
    # else:
    #     print("❌ Error al enviar notificación")


# ============================================================================
# EJEMPLO 5: Análisis de datos históricos
# ============================================================================
def ejemplo_analisis_historico():
    """Analiza el historial de convocatorias procesadas"""
    print("\n" + "=" * 60)
    print("EJEMPLO 5: Análisis de datos históricos")
    print("=" * 60)

    monitor = EUAPIMonitor()

    processed = monitor.processed_calls

    print(f"Total de convocatorias procesadas: {len(processed)}")

    if processed:
        # Contar por mes
        from collections import Counter
        from datetime import datetime

        meses = Counter()
        for call_data in processed.values():
            fecha = datetime.fromisoformat(call_data["processed_at"])
            mes = f"{fecha.year}-{fecha.month:02d}"
            meses[mes] += 1

        print("\nConvocatorias procesadas por mes:")
        for mes in sorted(meses.keys()):
            print(f"  {mes}: {meses[mes]}")

        # Palabras clave más frecuentes
        palabras = Counter()
        for call_data in processed.values():
            titulo = (call_data.get("title", "") or "").lower()
            for palabra in titulo.split():
                if len(palabra) > 4:  # Solo palabras largas
                    palabras[palabra] += 1

        print("\nPalabras clave más frecuentes:")
        for palabra, count in palabras.most_common(10):
            print(f"  {palabra}: {count}")


# ============================================================================
# EJEMPLO 6: Búsqueda multi-término con consolidación
# ============================================================================
def ejemplo_multibusqueda():
    """Realiza múltiples búsquedas y consolida resultados únicos"""
    print("\n" + "=" * 60)
    print("EJEMPLO 6: Búsqueda multi-término consolidada")
    print("=" * 60)

    monitor = EUAPIMonitor()

    terminos = [
        "Castilla-La Mancha",
        "Despoblación",
        "NextGenerationEU",
        "FEADER",
    ]

    todos_resultados = []
    urls_procesadas = set()

    for termino in terminos:
        print(f"\nBuscando: {termino}...")
        results = monitor.search_opportunities(termino)

        for result in results:
            url = result.get("url", "")
            if url not in urls_procesadas:
                todos_resultados.append(result)
                urls_procesadas.add(url)

    print(f"\n✅ Total de resultados únicos: {len(todos_resultados)}")
    print(f"   (De {len(terminos)} términos buscados)")


# ============================================================================
# EJEMPLO 7: Configurar alertas temáticas
# ============================================================================
def ejemplo_alertas_tematicas():
    """Crea alertas basadas en temas específicos"""
    print("\n" + "=" * 60)
    print("EJEMPLO 7: Alertas temáticas")
    print("=" * 60)

    monitor = EUAPIMonitor()

    # Definir temas y palabras clave asociadas
    temas = {
        "Turismo": ["turismo", "turista", "patrimonio", "cultura"],
        "Agricultura": ["agricultura", "ganadería", "agrícola", "rural"],
        "Juventud": ["jóvenes", "emprendimiento", "empleo joven", "educación"],
        "Mujer": ["mujer", "emprendedoras", "igualdad", "género"],
    }

    # Buscar convocatorias
    results = monitor.search_opportunities("Castilla-La Mancha")

    # Clasificar por tema
    convocatorias_por_tema = {tema: [] for tema in temas}

    for call in results:
        texto = f"{call.get('title', '')} {call.get('description', '')}".lower()

        for tema, palabras_clave in temas.items():
            if any(palabra in texto for palabra in palabras_clave):
                convocatorias_por_tema[tema].append(call)

    # Mostrar resultados por tema
    for tema, convocatorias in convocatorias_por_tema.items():
        if convocatorias:
            print(f"\n📌 {tema}: {len(convocatorias)} convocatorias")
            for call in convocatorias[:2]:
                print(f"   • {call.get('title', 'N/A')[:60]}")


# ============================================================================
# MAIN: Ejecutar ejemplos
# ============================================================================
def main():
    print("\n")
    print("╔" + "=" * 58 + "╗")
    print("║" + "EJEMPLOS DE USO AVANZADO".center(58) + "║")
    print("║" + "Monitor de Convocatorias Europeas".center(58) + "║")
    print("╚" + "=" * 58 + "╝")

    ejemplos = [
        ("Búsqueda personalizada", ejemplo_busqueda_personalizada),
        ("Procesamiento manual", ejemplo_procesamiento_manual),
        ("Exportar a CSV", ejemplo_exportar_csv),
        ("Notificación personalizada", ejemplo_notificacion_personalizada),
        ("Análisis histórico", ejemplo_analisis_historico),
        ("Búsqueda multi-término", ejemplo_multibusqueda),
        ("Alertas temáticas", ejemplo_alertas_tematicas),
    ]

    print("\nEjemplos disponibles:")
    for i, (nombre, _) in enumerate(ejemplos, 1):
        print(f"  {i}. {nombre}")

    try:
        opcion = input("\n¿Qué ejemplo deseas ejecutar? (1-7, o Enter para todos): ").strip()

        if opcion == "":
            # Ejecutar todos
            for nombre, func in ejemplos:
                try:
                    func()
                except Exception as e:
                    print(f"❌ Error en {nombre}: {e}")
        else:
            num = int(opcion) - 1
            if 0 <= num < len(ejemplos):
                ejemplos[num][1]()
            else:
                print("❌ Opción inválida")

    except KeyboardInterrupt:
        print("\n\nOperación cancelada")
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    main()
