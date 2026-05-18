# De Opdracht Semester 2 HBO-ICT BIM

![De-opdracht](de-opdracht.png)

## Hoe is deze repository ingericht

- Story-board. Bij Plan > Issues komen de  userstories te staan. Learning stories kopieer via de DLO naar je persoonlijke Learning Journey.
- Broncode in de map `app`. Dit is een kale Flask webapplicatie. Deze moet jij aanpassen.
- Documentatie in de map `docs`. In de docs vindt je alle informatie en hou je jouw portfolio bij dit project.
- Tests in de map `tests`. Hier schrijf jij jouw units-tests
- De `Dockerfile` en `docker-compose.yml` kan je gebruiken om een image van je applicatie te maken.
- Voor Deploying kan je gebruik maken van de `.gitlab-ci.yml` file.

## Installatie checklist

Volg zonodig de [set up](https://knowledgebase.hbo-ict-hva.nl/3_onderwijs/bim/). Vragen? Stel ze elkaar, vraag pas de studentenmentor als je er niet uitkomt en als die niet beschikbaar is een docent.

_Je kunt de applicatie pas starten nadat je de installatie geheel hebt doorlopen!_

- Opdracht omschrijving lezen
- VS-code installeren
- Python installeren
- Git installeren
- SSH-key toevoegen op Gitlab
- Project clonen vanaf Gitlab
- Virtual enviroment maken
- Database optuigen
- Docker installeren
- Opstarten applicatie


### Unit tests

Run tests met

```code
$ pytest
```

## Git remotes

In deze repository zijn de remotes expliciet benoemd als:

- `github` voor GitHub
- `gitlab` voor GitLab

Gebruik altijd expliciet:

```bash
git push github main
git push gitlab main
```

Zorg dat je beide remotes bijwerkt wanneer je wijzigingen op `main` hebt gemaakt.

## Studiehandleiding

In de Studiehandleiding op de DLO staat beschreven welke competenties je gaat ontwikkelen en wat de leeruitkomsten zijn voor dit blok.
