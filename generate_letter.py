import os

def escape_pdf_text(text: str) -> str:
    return text.replace('\\', '\\\\').replace('(', '\\(').replace(')', '\\)')

lines = [
    "Prénom Nom",
    "Adresse | Ville, Province",
    "Courriel | Téléphone",
    "",
    "12 mars 2024",
    "",
    "Direction des ressources humaines",
    "Tim Hortons",
    "",
    "Objet : Candidature au poste d'assistant gérant",
    "",
    "Madame, Monsieur,",
    "",
    "Fort de plusieurs années d'engagement dans l'organisation de rassemblements automobiles, je souhaite aujourd'hui mettre mon leadership et mon sens du service au profit de Tim Hortons en tant qu'assistant gérant.",
    "Lors de ces événements réunissant plus de 1 000 participants, j'ai coordonné une équipe de dix bénévoles, géré la logistique complète et garanti une expérience mémorable et sécuritaire pour chacun.",
    "Cette expérience m'a appris à planifier avec rigueur, à communiquer efficacement sous pression et à entretenir un climat d'équipe positif et motivant.",
    "",
    "Au-delà de la gestion opérationnelle, j'ai développé une forte capacité à anticiper les besoins des invités, à résoudre rapidement les imprévus et à offrir un accueil chaleureux, des qualités directement transférables à l'environnement dynamique des restaurants Tim Hortons.",
    "Je suis convaincu que mon sens de l'organisation, ma disponibilité et mon désir constant d'améliorer les processus contribueront à soutenir votre équipe et à assurer la satisfaction de la clientèle.",
    "",
    "Je vous remercie sincèrement de l'attention portée à ma candidature et serais ravi de discuter de vive voix de la valeur que je peux apporter à votre établissement.",
    "",
    "Veuillez agréer, Madame, Monsieur, l'expression de mes salutations distinguées.",
    "",
    "Prénom Nom"
]

content_lines = [escape_pdf_text(line if line else " ") for line in lines]


def build_text_stream() -> str:
    text_stream = ["BT", "/F1 12 Tf", "72 720 Td"]
    first = True
    for line in content_lines:
        if not first:
            text_stream.append("0 -18 Td")
        first = False
        text_stream.append(f"({line}) Tj")
    text_stream.append("ET")
    return "\n".join(text_stream) + "\n"


def build_pdf_bytes() -> bytes:
    text_bytes = build_text_stream().encode('utf-8')

    objects = []
    objects.append(b"<< /Type /Catalog /Pages 2 0 R >>")
    objects.append(b"<< /Type /Pages /Count 1 /Kids [3 0 R] >>")
    page_obj = (
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] /Contents 4 0 R "
        b"/Resources << /Font << /F1 5 0 R >> >> >>"
    )
    objects.append(page_obj)
    content_obj = (
        b"<< /Length "
        + str(len(text_bytes)).encode()
        + b" >>\nstream\n"
        + text_bytes
        + b"endstream\n"
    )
    objects.append(content_obj)
    objects.append(b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>")

    pdf = bytearray()
    pdf.extend(b"%PDF-1.4\n")
    offsets = [0]
    for i, obj in enumerate(objects, start=1):
        offsets.append(len(pdf))
        pdf.extend(f"{i} 0 obj\n".encode())
        pdf.extend(obj)
        pdf.extend(b"\nendobj\n")

    startxref = len(pdf)
    count = len(objects) + 1
    pdf.extend(b"xref\n")
    pdf.extend(f"0 {count}\n".encode())
    pdf.extend(b"0000000000 65535 f \n")
    for offset in offsets[1:]:
        pdf.extend(f"{offset:010d} 00000 n \n".encode())
    pdf.extend(b"trailer\n")
    pdf.extend(f"<< /Size {count} /Root 1 0 R >>\n".encode())
    pdf.extend(b"startxref\n")
    pdf.extend(f"{startxref}\n".encode())
    pdf.extend(b"%%EOF\n")

    return bytes(pdf)


if __name__ == "__main__":
    with open("lettre_presentation_tim_horton.pdf", "wb") as f:
        f.write(build_pdf_bytes())
