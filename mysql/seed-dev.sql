create table if not exists historico_escolar (
    cpf varchar(14) not null,
    student_id int not null,
    nome varchar(10),
    disciplina varchar(50) not null,
    faltas int not null,
    nota_final int not null
);

insert into historico_escolar
    (cpf, student_id, nome, disciplina, faltas, nota_final)
values
    ("666.666.666-66", 6666, "ANA", "biossegurança", 0, 60),
    ("666.666.666-66", 6666, "ANA", "cosmetologia", 1, 95),
    ("777.777.777-77", 7777, "PEDRO", "biossegurança", 0, 54),
    ("777.777.777-77", 7777, "PEDRO", "cosmetologia", 1, 100),
    ("888.888.888-88", 8888, "MARIA", "biossegurança", 0, 75),
    ("888.888.888-88", 8888, "MARIA", "cosmetologia", 1, 65),
    ("999.999.999-99", 9999, "JOÃO", "biossegurança", 0, 70),
    ("999.999.999-99", 9999, "JOÃO", "cosmetologia", 1, 80);
