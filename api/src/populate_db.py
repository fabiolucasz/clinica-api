from src.database.connection import SessionLocal
from src.models import models
from datetime import datetime, timedelta
from src.models.models import Calendario, CalendarioClinica

def create_estados():
    """Cria estados brasileiros"""
    print("📍 Criando estados...")
    try:
        estados = [
            ('Acre', 'AC'), ('Alagoas', 'AL'), ('Amapá', 'AP'), ('Amazonas', 'AM'),
            ('Bahia', 'BA'), ('Ceará', 'CE'), ('Distrito Federal', 'DF'), ('Espírito Santo', 'ES'),
            ('Goiás', 'GO'), ('Maranhão', 'MA'), ('Mato Grosso', 'MT'), ('Mato Grosso do Sul', 'MS'),
            ('Minas Gerais', 'MG'), ('Pará', 'PA'), ('Paraíba', 'PB'), ('Paraná', 'PR'),
            ('Pernambuco', 'PE'), ('Piauí', 'PI'), ('Rio de Janeiro', 'RJ'), ('Rio Grande do Norte', 'RN'),
            ('Rio Grande do Sul', 'RS'), ('Rondônia', 'RO'), ('Roraima', 'RR'), ('Santa Catarina', 'SC'),
            ('São Paulo', 'SP'), ('Sergipe', 'SE'), ('Tocantins', 'TO')
        ]
        
        db = SessionLocal()
        try:
            for nome, uf in estados:
                estado = db.query(models.Estados).filter(models.Estados.nome == nome).first()
                if not estado:
                    estado = models.Estados(nome=nome, uf=uf)
                    db.add(estado)
                    print(f"  ✅ Estado criado: {nome}")
            db.commit()
            return True
        finally:
            db.close()
    except Exception as e:
        print(f"Erro: {e}")
        return False

def create_tipos_conselho():
    """Cria tipos de conselho"""
    print("🏥 Criando tipos de conselho...")
    try:
        tipos = ['CRM', 'CRP', 'CRN', 'CREFITO']
        
        db = SessionLocal()
        try:
            for tipo in tipos:
                conselho = db.query(models.Tipo_conselho).filter(models.Tipo_conselho.nome == tipo).first()
                if not conselho:
                    conselho = models.Tipo_conselho(nome=tipo)
                    db.add(conselho)
                    print(f"  ✅ Tipo de conselho criado: {tipo}")
            db.commit()
            return True
        finally:
            db.close()
    except Exception as e:
        print(f"Erro: {e}")
        return False

def create_especialidades():
    """Cria especialidades médicas"""
    print("⚕️ Criando especialidades...")
    try:
        especialidades_data = [
            'Cardiologista', 'Dermatologista', 'Ginecologista', 'Oftalmologista',
            'Ortopedista', 'Pediatra', 'Psiquiatra', 'Urologista', 'Psicólogo(a)'
        ]
        
        db = SessionLocal()
        try:
            for esp in especialidades_data:
                especialidade = db.query(models.Especialidades).filter(models.Especialidades.nome == esp).first()
                if not especialidade:
                    especialidade = models.Especialidades(nome=esp)
                    db.add(especialidade)
                    print(f"  ✅ Especialidade criada: {esp}")
            db.commit()
            return True
        finally:
            db.close()
    except Exception as e:
        print(f"Erro: {e}")
        return False

def turnos():
    """Cria turnos"""
    print("⏰ Criando turnos...")
    try:
        turnos_data = [
            {'nome': 'Manhã', 'hora_inicio': '08:00', 'hora_fim': '12:00'},
            {'nome': 'Tarde', 'hora_inicio': '13:00', 'hora_fim': '17:00'},
            {'nome': 'Noite', 'hora_inicio': '17:00', 'hora_fim': '21:00'},
        ]
        
        db = SessionLocal()
        try:
            for turno in turnos_data:
                turno_obj = db.query(models.Turnos).filter(models.Turnos.nome == turno['nome']).first()
                if not turno_obj:
                    turno_obj = models.Turnos(**turno)
                    db.add(turno_obj)
                    print(f"  ✅ Turno criado: {turno['nome']}")
            db.commit()
            return True
        finally:
            db.close()
    except Exception as e:
        print(f"Erro: {e}")
        return False

def popular_calendario(ano_inicio=2026, ano_fim=2030):
    """Popula tabela calendario com datas no formato ISO"""
    db = SessionLocal()
    
    try:
        # Limpar dados existentes
        db.query(Calendario).delete()
        
        data_inicio = datetime(ano_inicio, 1, 1)
        data_fim = datetime(ano_fim, 12, 31)
        
        dias_semana = ['domingo', 'segunda-feira', 'terca-feira', 'quarta-feira', 'quinta-feira', 'sexta-feira', 'sabado']
        meses = ['janeiro', 'fevereiro', 'marco', 'abril', 'maio', 'junho', 
                'julho', 'agosto', 'setembro', 'outubro', 'novembro', 'dezembro']
        
        data_atual = data_inicio
        
        while data_atual <= data_fim:
            # Verificar se é dia útil (segunda-sexta)
            dia_util = data_atual.weekday() in [1, 2, 3, 4, 5]  # 1=segunda, 5=sexta
            
            calendario = Calendario(
                data_iso=data_atual.strftime('%Y-%m-%d').split(' ')[0],
                data_br=data_atual.strftime('%d/%m/%Y').split(' ')[0],
                data_datetime=data_atual,
                ano=data_atual.year,
                mes=data_atual.month,
                dia=data_atual.day,
                dia_semana=data_atual.weekday(),
                dia_semana_nome=dias_semana[data_atual.weekday()],
                mes_nome=meses[data_atual.month - 1],
                bimestre=(data_atual.month - 1) // 2 + 1,
                trimestre=(data_atual.month - 1) // 3 + 1,
                quadrimestre=(data_atual.month - 1) // 4 + 1,
                semestre=(data_atual.month - 1) // 6 + 1,
                semana_ano=data_atual.isocalendar()[1],
                dia_util=dia_util
            )
            
            db.add(calendario)
            data_atual += timedelta(days=1)
        
        db.commit()
        print(f"✅ Calendário populado: {ano_inicio} a {ano_fim}")
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        db.rollback()
    finally:
        db.close()


def popular_calendario_clinica():
    """Popula tabela calendario_clinica para todas as clínicas com feriados nacionais"""
    db = SessionLocal()
    
    try:
        # Limpar dados existentes
        db.query(CalendarioClinica).delete()
        
        feriados_nacionais = [
            {"nome": "Confraternização Universal", "mes": 1, "dia": 1},
            {"nome": "Tiradentes", "mes": 4, "dia": 21},
            {"nome": "Dia do Trabalhador", "mes": 5, "dia": 1},
            {"nome": "Corpus Christi", "mes": 6, "dia": 19},
            {"nome": "Independência do Brasil", "mes": 9, "dia": 7},
            {"nome": "Nossa Senhora Aparecida", "mes": 10, "dia": 12},
            {"nome": "Finados", "mes": 11, "dia": 2},
            {"nome": "Proclamação da República", "mes": 11, "dia": 15},
            {"nome": "Consciência Negra", "mes": 11, "dia": 20},
            {"nome": "Natal", "mes": 12, "dia": 25},
        ]
        
        # Buscar todas as clínicas cadastradas
        clinicas = db.query(models.Clinicas).all()
        ano_atual = datetime.now().year
        
        print(f"🏥 Criando calendário para {len(clinicas)} clínicas...")
        
        for clinica in clinicas:
            print(f"  📅 Processando clínica: {clinica.nome} (ID: {clinica.id})")
            
            # Buscar todos os dias do ano corrente
            dias_ano = db.query(Calendario).filter(Calendario.ano == ano_atual).all()
            
            for dia in dias_ano:
                # Verificar se é feriado nacional
                feriado = False
                nome_feriado = None
                
                for feriado_nacional in feriados_nacionais:
                    if dia.mes == feriado_nacional["mes"] and dia.dia == feriado_nacional["dia"]:
                        feriado = True
                        nome_feriado = feriado_nacional["nome"]
                        break
                
                # Se for feriado, criar registro na tabela calendario_clinica
                if feriado:
                    calendario_clinica = CalendarioClinica(
                        clinica_id=clinica.id,
                        data_feriado=dia.id,
                        nome_feriado=nome_feriado,
                        aberta=False  # Clínica fechada em feriados
                    )
                    db.add(calendario_clinica)
                    print(f"    🎉 Feriado adicionado: {nome_feriado} em {dia.data_iso}")
        
        db.commit()
        print(f"✅ Calendário clínica populado para {len(clinicas)} clínicas - Ano {ano_atual}")
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        db.rollback()
    finally:
        db.close()

def create_horario_consulta():
    """Cria horários de consultas conforme especificado"""
    print("⏰ Criando horários de consultas...")
    try:
        db = SessionLocal()
        try:
            # Verificar se já existem horários
            existing_count = db.query(models.HorariosConsultas).count()
            if existing_count > 0:
                print(f"  ℹ️  Já existem {existing_count} horários cadastrados. Pulando criação.")
                return True
            
            # Dados conforme especificado
            horarios_data = [
                # Turno 1 - Manhã (08:00-12:00)
                (1, "08:00", "09:00", 1),
                (2, "09:00", "10:00", 1),
                (3, "10:00", "11:00", 1),
                (4, "11:00", "12:00", 1),
                
                # Turno 2 - Tarde (13:00-17:00)
                (5, "13:00", "14:00", 2),
                (6, "14:00", "15:00", 2),
                (7, "15:00", "16:00", 2),
                (8, "16:00", "17:00", 2),
                
                # Turno 3 - Noite (18:00-22:00)
                (9, "18:00", "19:00", 3),
                (10, "19:00", "20:00", 3),
                (11, "20:00", "21:00", 3),
                (12, "21:00", "22:00", 3),
            ]
            
            for id, hora_inicio, hora_fim, turno_id in horarios_data:
                # Verificar se já existe
                existing = db.query(models.HorariosConsultas).filter(
                    models.HorariosConsultas.id == id
                ).first()
                
                if not existing:
                    horario = models.HorariosConsultas(
                        id=id,
                        hora_inicio=hora_inicio,
                        hora_fim=hora_fim,
                        turno=turno_id
                    )
                    db.add(horario)
                    print(f"  ✅ Horário criado: {hora_inicio}-{hora_fim} (Turno {turno_id})")
            
            db.commit()
            print(f"  ✅ {len(horarios_data)} horários de consultas criados com sucesso!")
            return True
            
        finally:
            db.close()
    except Exception as e:
        print(f"Erro ao criar horários de consultas: {e}")
        return False

def populate_database():
    """Função principal para popular o banco de dados"""
    print("🚀 Iniciando população do banco de dados...")
    
    # Criar dados básicos
    create_estados()
    create_tipos_conselho()
    create_especialidades()
    turnos()
    create_horario_consulta()  # Adicionado!
    popular_calendario()
    popular_calendario_clinica()
    
    print("✅ Banco de dados populado com sucesso!")
if __name__ == '__main__':
    populate_database()