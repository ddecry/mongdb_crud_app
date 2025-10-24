# main.py
import sys
import json
from mongodb_manager import MongoDBManager
from redis_cache import RedisCache

CACHE_KEY_ALL = "students:all"

def print_student(s):
    print(f"ID: {s.get('id')}")
    print(f"Nome: {s.get('name')}")
    print(f"Nascimento: {s.get('birthdate')}")
    print(f"E-mail: {s.get('email')}")
    print(f"Curso: {s.get('course')}")
    print(f"Matrícula: {s.get('enrollment_number')}")
    print("-" * 40)

def input_student_data(existing=None):
    # existing: dict para pré-preencher (usado no update)
    existing = existing or {}
    name = input(f"Nome [{existing.get('name','')}]: ").strip() or existing.get('name')
    birthdate = input(f"Nascimento (YYYY-MM-DD) [{existing.get('birthdate','')}]: ").strip() or existing.get('birthdate')
    email = input(f"E-mail [{existing.get('email','')}]: ").strip() or existing.get('email')
    course = input(f"Curso [{existing.get('course','')}]: ").strip() or existing.get('course')
    enrollment_number = input(f"Matrícula [{existing.get('enrollment_number','')}]: ").strip() or existing.get('enrollment_number')
    data = {
        "name": name,
        "birthdate": birthdate,
        "email": email,
        "course": course,
        "enrollment_number": enrollment_number
    }
    # remove None/empty
    return {k: v for k, v in data.items() if v is not None and v != ""}

def create(manager: MongoDBManager, cache: RedisCache):
    print("\n== Criar novo aluno ==")
    data = input_student_data()
    if not data.get("name"):
        print("Nome é obrigatório.")
        return
    try:
        new_id = manager.create_student(data)
        # invalidar cache
        cache.delete(CACHE_KEY_ALL)
        print(f"Aluno criado com ID: {new_id}")
    except Exception as e:
        print(f"Erro ao criar aluno: {e}")

def list_all(manager: MongoDBManager, cache: RedisCache):
    print("\n== Listar alunos ==")
    cached = cache.get(CACHE_KEY_ALL)
    if cached is not None:
        print(f"(Usando cache - expira em segundos configurados)\nTotal: {len(cached)}")
        for s in cached:
            print_student(s)
        return
    try:
        students = manager.list_students()
        cache.set(CACHE_KEY_ALL, students)
        print(f"Total: {len(students)}")
        for s in students:
            print_student(s)
    except Exception as e:
        print(f"Erro ao listar: {e}")

def view_student(manager: MongoDBManager):
    sid = input("ID do aluno: ").strip()
    student = manager.get_student(sid)
    if not student:
        print("Aluno não encontrado.")
        return
    print_student(student)

def update_student(manager: MongoDBManager, cache: RedisCache):
    sid = input("ID do aluno para atualizar: ").strip()
    student = manager.get_student(sid)
    if not student:
        print("Aluno não encontrado.")
        return
    print("Deixe em branco para manter o valor atual.")
    updates = input_student_data(student)
    if not updates:
        print("Nada para atualizar.")
        return
    try:
        ok = manager.update_student(sid, updates)
        if ok:
            cache.delete(CACHE_KEY_ALL)
            print("Atualizado com sucesso.")
        else:
            print("Nenhuma modificação realizada.")
    except Exception as e:
        print(f"Erro ao atualizar: {e}")

def delete_student(manager: MongoDBManager, cache: RedisCache):
    sid = input("ID do aluno para excluir: ").strip()
    confirm = input("Confirma exclusão? (s/N): ").strip().lower()
    if confirm != "s":
        print("Exclusão cancelada.")
        return
    try:
        ok = manager.delete_student(sid)
        if ok:
            cache.delete(CACHE_KEY_ALL)
            print("Aluno excluído.")
        else:
            print("Aluno não encontrado ou não excluído.")
    except Exception as e:
        print(f"Erro ao excluir: {e}")

def main_loop():
    try:
        mongo = MongoDBManager()
    except Exception as e:
        print(e)
        sys.exit(1)
    cache = RedisCache()

    menu = """
======== Cadastro de Alunos (Terminal) ========
1) Cadastrar aluno
2) Listar todos os alunos (usa cache Redis)
3) Ver aluno por ID
4) Atualizar aluno
5) Excluir aluno
0) Sair
===============================================
Escolha: """
    while True:
        choice = input(menu).strip()
        if choice == "1":
            create(mongo, cache)
        elif choice == "2":
            list_all(mongo, cache)
        elif choice == "3":
            view_student(mongo)
        elif choice == "4":
            update_student(mongo, cache)
        elif choice == "5":
            delete_student(mongo, cache)
        elif choice == "0":
            print("Tchau!")
            break
        else:
            print("Opção inválida. Tente novamente.")

if __name__ == "__main__":
    main_loop()