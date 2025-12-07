from pathlib import Path
from typing import Optional, Dict, List
import pandas as pd
import datetime
import io

from src.models.config import Config
from src.utils.exceptions import DataProcessingError
from src.utils.logger import get_logger

logger = get_logger(__name__)


class ExportService:
    def __init__(self, config: Config, output_dir: Path):
        self.config = config
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"ExportService zainicjalizowany z katalogiem wyjściowym: {output_dir}")
    
    def export_to_csv(
        self, 
        df: pd.DataFrame, 
        filename: str = "indeks_branz.csv"
    ) -> Path:
        filepath = self.output_dir / filename
        
        try:
            if filepath.exists():
                try:
                    with open(filepath, 'a', encoding='utf-8-sig'):
                        pass
                except PermissionError:
                    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                    backup_filename = f"{filepath.stem}_{timestamp}{filepath.suffix}"
                    filepath = self.output_dir / backup_filename
                    logger.warning(
                        f"Oryginalny plik jest zablokowany, używam nazwy kopii zapasowej: {backup_filename}"
                    )
            
            logger.info(f"Eksportowanie do CSV: {filepath}")
            df.to_csv(filepath, index=False, encoding='utf-8-sig')
            logger.info(f"Pomyślnie wyeksportowano CSV: {filepath}")
            return filepath
        except PermissionError as e:
            error_msg = (
                f"Odmowa dostępu: {filepath}. "
                "Zamknij plik, jeśli jest otwarty w Excelu lub innej aplikacji."
            )
            logger.error(error_msg)
            raise DataProcessingError(error_msg) from e
        except Exception as e:
            error_msg = f"Błąd eksportowania do CSV: {e}"
            logger.error(error_msg)
            raise DataProcessingError(error_msg) from e
    
    def export_to_excel(
        self, 
        df: pd.DataFrame,
        main_sheet_name: str = "Indeks Branż",
        filename: str = "indeks_branz.xlsx",
        additional_sheets: Optional[dict] = None
    ) -> Path:
        filepath = self.output_dir / filename
        
        try:
            if filepath.exists():
                try:
                    import openpyxl
                    wb = openpyxl.load_workbook(filepath)
                    wb.close()
                except PermissionError:
                    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                    backup_filename = f"{filepath.stem}_{timestamp}{filepath.suffix}"
                    filepath = self.output_dir / backup_filename
                    logger.warning(
                        f"Oryginalny plik jest zablokowany, używam nazwy kopii zapasowej: {backup_filename}"
                    )
                except Exception:
                    pass
            
            logger.info(f"Eksportowanie do Excel: {filepath}")
            
            with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name=main_sheet_name, index=False)
                
                if additional_sheets:
                    for sheet_name, sheet_df in additional_sheets.items():
                        sheet_df.to_excel(writer, sheet_name=sheet_name, index=False)
                        logger.debug(f"Dodano arkusz: {sheet_name}")
            
            logger.info(f"Pomyślnie wyeksportowano Excel: {filepath}")
            return filepath
        except PermissionError as e:
            error_msg = (
                f"Odmowa dostępu: {filepath}. "
                "Zamknij plik, jeśli jest otwarty w Excelu lub innej aplikacji."
            )
            logger.error(error_msg)
            raise DataProcessingError(error_msg) from e
        except Exception as e:
            error_msg = f"Błąd eksportowania do Excel: {e}"
            logger.error(error_msg)
            raise DataProcessingError(error_msg) from e
    
    def export_results(
        self,
        results_df: pd.DataFrame,
        top_10_df: Optional[pd.DataFrame] = None,
        growing_df: Optional[pd.DataFrame] = None,
        risky_df: Optional[pd.DataFrame] = None
    ) -> dict:
        logger.info("Eksportowanie wszystkich wyników")
        
        csv_path = self.export_to_csv(results_df)
        
        additional_sheets = {}
        if top_10_df is not None:
            additional_sheets["Top 10"] = top_10_df
        if growing_df is not None:
            additional_sheets["Najszybciej rozwijające się"] = growing_df
        if risky_df is not None:
            additional_sheets["Najbardziej ryzykowne"] = risky_df
        
        excel_path = self.export_to_excel(
            results_df,
            additional_sheets=additional_sheets if additional_sheets else None
        )
        
        return {
            "csv": csv_path,
            "excel": excel_path
        }
    
    def export_to_pdf(self, data: Dict, filename: str = "raport.pdf") -> bytes:
        try:
            from reportlab.lib import colors
            from reportlab.lib.pagesizes import A4
            from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib.units import inch
            from reportlab.pdfgen import canvas
            from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
            from reportlab.lib.utils import simpleSplit
            import html
            
            buffer = io.BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=A4, 
                                   rightMargin=0.75*inch, leftMargin=0.75*inch,
                                   topMargin=0.75*inch, bottomMargin=0.75*inch)
            story = []
            styles = getSampleStyleSheet()
            
            def safe_text(text):
                if text is None:
                    return ''
                return str(text)
            
            primary_color = colors.HexColor('#667eea')
            secondary_color = colors.HexColor('#764ba2')
            accent_color = colors.HexColor('#f093fb')
            dark_grey = colors.HexColor('#2c3e50')
            light_grey = colors.HexColor('#ecf0f1')
            
            primary_hex = '#667eea'
            secondary_hex = '#764ba2'
            accent_hex = '#f093fb'
            
            try:
                from reportlab.pdfbase import pdfmetrics
                from reportlab.pdfbase.ttfonts import TTFont
                try:
                    pdfmetrics.registerFont(TTFont('DejaVuSans', 'DejaVuSans.ttf'))
                    pdfmetrics.registerFont(TTFont('DejaVuSans-Bold', 'DejaVuSans-Bold.ttf'))
                    base_font = 'DejaVuSans'
                    bold_font = 'DejaVuSans-Bold'
                except:
                    base_font = 'Helvetica'
                    bold_font = 'Helvetica-Bold'
            except:
                base_font = 'Helvetica'
                bold_font = 'Helvetica-Bold'
            
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Title'],
                fontSize=28,
                textColor=primary_color,
                spaceAfter=30,
                alignment=TA_CENTER,
                fontName=bold_font
            )
            
            heading_style = ParagraphStyle(
                'CustomHeading',
                parent=styles['Heading1'],
                fontSize=18,
                textColor=dark_grey,
                spaceAfter=12,
                spaceBefore=20,
                fontName=bold_font
            )
            
            subheading_style = ParagraphStyle(
                'CustomSubheading',
                parent=styles['Heading2'],
                fontSize=14,
                textColor=secondary_color,
                spaceAfter=8,
                spaceBefore=12,
                fontName=bold_font
            )
            
            info_style = ParagraphStyle(
                'InfoStyle',
                parent=styles['Normal'],
                fontSize=10,
                textColor=colors.HexColor('#7f8c8d'),
                alignment=TA_CENTER,
                fontName=base_font
            )
            
            normal_style = ParagraphStyle(
                'NormalUTF8',
                parent=styles['Normal'],
                fontName=base_font
            )
            
            story.append(Spacer(1, 0.3*inch))
            story.append(Paragraph("INDEKS BRANŻ", title_style))
            story.append(Paragraph("Raport Analizy Sektora", info_style))
            story.append(Spacer(1, 0.4*inch))
            
            if 'sector' in data:
                sector = data['sector']
                
                branch_name = safe_text(sector.get('branch_name', 'N/A'))
                pkd_code = safe_text(str(sector.get('pkd_code', 'N/A')))
                category = safe_text(sector.get('category', 'N/A'))
                
                header_data = [
                    [Paragraph(f"<b><font color='{primary_hex}'>Sektor:</font></b>", normal_style),
                     Paragraph(f"<font size=12>{html.escape(branch_name)}</font>", normal_style)],
                    [Paragraph(f"<b><font color='{primary_hex}'>Kod PKD:</font></b>", normal_style),
                     Paragraph(f"<font size=12>{html.escape(pkd_code)}</font>", normal_style)],
                    [Paragraph(f"<b><font color='{primary_hex}'>Kategoria:</font></b>", normal_style),
                     Paragraph(f"<font size=12>{html.escape(category)}</font>", normal_style)],
                ]
                
                header_table = Table(header_data, colWidths=[2*inch, 4*inch])
                header_table.setStyle(TableStyle([
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    ('LEFTPADDING', (0, 0), (-1, -1), 10),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 10),
                    ('TOPPADDING', (0, 0), (-1, -1), 8),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                ]))
                story.append(header_table)
                story.append(Spacer(1, 0.3*inch))
                
                index_value = sector.get('final_index', 0)
                if index_value >= 0.6:
                    index_color = primary_color
                    index_hex = primary_hex
                elif index_value >= 0.4:
                    index_color = accent_color
                    index_hex = accent_hex
                else:
                    index_color = colors.HexColor('#e74c3c')
                    index_hex = '#e74c3c'
                
                index_box = Table([
                    [Paragraph(f"<b><font size=16 color='{index_hex}'>Indeks Końcowy</font></b>", normal_style)],
                    [Paragraph(f"<font size=24 color='{index_hex}'><b>{index_value:.3f}</b></font>", normal_style)]
                ], colWidths=[6.5*inch], repeatRows=0)
                index_box.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, -1), light_grey),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    ('LEFTPADDING', (0, 0), (-1, -1), 20),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 20),
                    ('TOPPADDING', (0, 0), (-1, -1), 15),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 15),
                    ('BOX', (0, 0), (-1, -1), 2, index_color),
                    ('ROWBACKGROUNDS', (0, 0), (-1, -1), [light_grey, colors.white])
                ]))
                story.append(index_box)
                story.append(Spacer(1, 0.4*inch))
                
                story.append(Paragraph("Wskaźniki Kondycji", heading_style))
                
                metrics_data = [
                    [Paragraph('Wskaźnik', normal_style), Paragraph('Wartość', normal_style), Paragraph('Procent', normal_style)],
                    [Paragraph('Wielkość', normal_style), Paragraph(f"{sector.get('size_score', 0):.3f}", normal_style), Paragraph(f"{sector.get('size_score', 0)*100:.1f}%", normal_style)],
                    [Paragraph('Rozwój', normal_style), Paragraph(f"{sector.get('growth_score', 0):.3f}", normal_style), Paragraph(f"{sector.get('growth_score', 0)*100:.1f}%", normal_style)],
                    [Paragraph('Rentowność', normal_style), Paragraph(f"{sector.get('profitability_score', 0):.3f}", normal_style), Paragraph(f"{sector.get('profitability_score', 0)*100:.1f}%", normal_style)],
                    [Paragraph('Zadłużenie', normal_style), Paragraph(f"{sector.get('debt_score', 0):.3f}", normal_style), Paragraph(f"{sector.get('debt_score', 0)*100:.1f}%", normal_style)],
                    [Paragraph('Ryzyko', normal_style), Paragraph(f"{sector.get('risk_score', 0):.3f}", normal_style), Paragraph(f"{sector.get('risk_score', 0)*100:.1f}%", normal_style)],
                ]
                
                metrics_table = Table(metrics_data, colWidths=[2.5*inch, 2*inch, 2*inch])
                metrics_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), primary_color),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    ('FONTNAME', (0, 0), (-1, 0), bold_font),
                    ('FONTSIZE', (0, 0), (-1, 0), 12),
                    ('FONTSIZE', (0, 1), (-1, -1), 10),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('TOPPADDING', (0, 0), (-1, 0), 12),
                    ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, light_grey]),
                    ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#bdc3c7')),
                    ('LEFTPADDING', (0, 0), (-1, -1), 10),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 10),
                    ('TOPPADDING', (0, 1), (-1, -1), 8),
                    ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
                ]))
                story.append(metrics_table)
                story.append(Spacer(1, 0.3*inch))
                
                story.append(Paragraph("Dodatkowe Metryki", heading_style))
                
                additional_metrics = []
                if sector.get('revenue_growth_yoy') is not None:
                    additional_metrics.append([Paragraph('Wzrost przychodów (YoY)', normal_style), Paragraph(f"{sector.get('revenue_growth_yoy', 0)*100:.2f}%", normal_style)])
                if sector.get('profit_growth_yoy') is not None:
                    additional_metrics.append([Paragraph('Wzrost zysku (YoY)', normal_style), Paragraph(f"{sector.get('profit_growth_yoy', 0)*100:.2f}%", normal_style)])
                if sector.get('profit_margin') is not None:
                    additional_metrics.append([Paragraph('Marża zysku', normal_style), Paragraph(f"{sector.get('profit_margin', 0)*100:.2f}%", normal_style)])
                if sector.get('debt_to_assets') is not None:
                    additional_metrics.append([Paragraph('Zadłużenie do aktywów', normal_style), Paragraph(f"{sector.get('debt_to_assets', 0)*100:.2f}%", normal_style)])
                if sector.get('bankruptcy_rate') is not None:
                    additional_metrics.append([Paragraph('Wskaźnik upadłości', normal_style), Paragraph(f"{sector.get('bankruptcy_rate', 0)*100:.2f}%", normal_style)])
                if sector.get('num_companies') is not None:
                    additional_metrics.append([Paragraph('Liczba przedsiębiorstw', normal_style), Paragraph(f"{int(sector.get('num_companies', 0)):,}", normal_style)])
                
                if additional_metrics:
                    additional_data = [[Paragraph('Metryka', normal_style), Paragraph('Wartość', normal_style)]] + additional_metrics
                    additional_table = Table(additional_data, colWidths=[4*inch, 2.5*inch])
                    additional_table.setStyle(TableStyle([
                        ('BACKGROUND', (0, 0), (-1, 0), secondary_color),
                        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                        ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
                        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                        ('FONTNAME', (0, 0), (-1, 0), bold_font),
                        ('FONTSIZE', (0, 0), (-1, 0), 11),
                        ('FONTSIZE', (0, 1), (-1, -1), 10),
                        ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
                        ('TOPPADDING', (0, 0), (-1, 0), 10),
                        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, light_grey]),
                        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#bdc3c7')),
                        ('LEFTPADDING', (0, 0), (-1, -1), 12),
                        ('RIGHTPADDING', (0, 0), (-1, -1), 12),
                        ('TOPPADDING', (0, 1), (-1, -1), 7),
                        ('BOTTOMPADDING', (0, 1), (-1, -1), 7),
                    ]))
                    story.append(additional_table)
                
                story.append(Spacer(1, 0.4*inch))
                
                footer_text = f"Wygenerowano: {datetime.datetime.now().strftime('%d.%m.%Y %H:%M')} | Indeks Branż API"
                story.append(Paragraph(f"<font size=8 color='#95a5a6'>{footer_text}</font>", info_style))
            
            def add_page_number(canvas_obj, doc):
                canvas_obj.saveState()
                try:
                    canvas_obj.setFont(base_font, 9)
                except:
                    canvas_obj.setFont('Helvetica', 9)
                page_num = canvas_obj.getPageNumber()
                text = f"Strona {page_num}"
                canvas_obj.setFillColor(colors.HexColor('#95a5a6'))
                try:
                    canvas_obj.drawRightString(7.25*inch, 0.5*inch, text)
                except UnicodeEncodeError:
                    canvas_obj.drawRightString(7.25*inch, 0.5*inch, f"Page {page_num}")
                canvas_obj.restoreState()
            
            doc.build(story, onFirstPage=add_page_number, onLaterPages=add_page_number)
            buffer.seek(0)
            return buffer.getvalue()
        except ImportError:
            logger.warning("reportlab nie jest zainstalowany, eksport PDF niedostępny")
            raise DataProcessingError("Eksport PDF wymaga biblioteki reportlab")
        except Exception as e:
            logger.error(f"Błąd eksportowania do PDF: {e}")
            raise DataProcessingError(f"Błąd eksportowania do PDF: {str(e)}")
    
    def export_chart_as_image(self, chart_html: str, filename: str = "chart.png") -> bytes:
        try:
            import plotly.graph_objects as go
            from plotly.io import to_image
            
            logger.warning("Eksport wykresu jako obraz wymaga implementacji")
            return b""
        except Exception as e:
            logger.error(f"Błąd eksportowania wykresu: {e}")
            raise DataProcessingError(f"Błąd eksportowania wykresu: {str(e)}")
