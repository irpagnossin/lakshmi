Esta pasta deve conter arquivos `csv` com o seguinte formato:

```
student_id
999
888
777
```

Esses são os ID dos alunos que serão avaliados e cadastrados como candidatos no [lakshmi-api](../lakshmi-api/README.md).

Esses alunos devem pertencer ao **mesmo curso e currículo**, de modo que cada arquivo `csv` representará, tipicamente, uma turma: `turma_1.csv`, `turma_2.csv` etc. Ainda assim, essa organização é opcional, pois todos os ID serão cadastrados.

A restrição de "mesmo currículo" é importante para garantir a consistência no mapeamento entre disciplinas e competências; e a restrição "mesmo curso" é importante porque esse curso tipicamente estará associado a uma carreira do `lakshmi-api`. Por exemplo, o curso de Enfermagem estará associado à carreira "enfermagem".

obs.: os arquivos [turma_1.csv](./turma_1.csv) e [turma_2.csv](./turma_2.csv) são exemplos fictícios. Apague-os antes de usar este projeto.
