# GoalStats – οδηγίες εγκατάστασης

Στατικό site που δείχνει γκολ υπέρ / κατά για τα επόμενα παιχνίδια σε 22 ευρωπαϊκά πρωταθλήματα. Ενημερώνεται μόνο του κάθε μέρα από το football-data.co.uk.

## Τι περιέχει

| Αρχείο | Τι κάνει |
|---|---|
| `index.html` | Η σελίδα (φίλτρα, πίνακας, ταξινόμηση). |
| `data/matches.csv` | Όλα τα αποτελέσματα της σεζόν. |
| `data/fixtures.csv` | Τα επόμενα παιχνίδια με αποδόσεις. |
| `data/updated.txt` | Η ημερομηνία της τελευταίας ενημέρωσης. |
| `scripts/update_data.py` | Κατεβάζει τα νέα αρχεία και ξαναφτιάχνει τα `data/`. |
| `.github/workflows/update-data.yml` | Τρέχει το script κάθε μέρα στις 05:17 UTC (07:17 ώρα Κύπρου). |

## 1. Ανέβασμα στο GitHub (~10 λεπτά, δωρεάν)

1. Φτιάξε λογαριασμό στο https://github.com.
2. Πάτα **New repository**, δώσε όνομα (π.χ. `goalstats`), επίλεξε **Public**, πάτα **Create repository**.
3. Πάτα **uploading an existing file** και σύρε **όλα** τα αρχεία και τους φακέλους από το zip (μαζί με τον φάκελο `.github`).
   - Σε Mac ο φάκελος `.github` είναι κρυφός: στο Finder πάτα `Cmd + Shift + .` για να φανεί.
   - Πάτα **Commit changes**.

## 2. Ενεργοποίηση του site

1. Στο repository: **Settings → Pages**.
2. Στο **Source** διάλεξε **Deploy from a branch**, branch **main**, φάκελο **/ (root)**, πάτα **Save**.
3. Σε 1–2 λεπτά το site είναι στο `https://<το-username-σου>.github.io/goalstats/`.

## 3. Ενεργοποίηση της αυτόματης ενημέρωσης

1. **Settings → Actions → General → Workflow permissions**: διάλεξε **Read and write permissions**, πάτα **Save**.
2. Πήγαινε στην καρτέλα **Actions**, διάλεξε **Update data**, πάτα **Run workflow**.
3. Σε ~1 λεπτό πρέπει να δεις πράσινο ✓. Από εκεί και πέρα τρέχει μόνο του κάθε μέρα.
4. **Έλεγξε μία φορά το link του προγράμματος:** στο https://www.football-data.co.uk/matches.php δες ότι το αρχείο «upcoming fixtures» είναι στο `https://www.football-data.co.uk/fixtures.csv`. Αν είναι αλλού, άλλαξε τη γραμμή `FIXTURES_URL` στο `scripts/update_data.py`.

Αν κάποια μέρα το football-data.co.uk δεν απαντήσει, το script κρατάει τα παλιά δεδομένα και ξαναδοκιμάζει την επόμενη μέρα.

## 4. Δικό σου .com

1. Αγόρασε το domain (π.χ. Cloudflare, Namecheap, ~€10–15/χρόνο).
2. Στο GitHub: **Settings → Pages → Custom domain**, γράψε `www.το-domain-σου.com`, πάτα **Save**.
3. Στις ρυθμίσεις DNS του domain πρόσθεσε:
   - `CNAME` με όνομα `www` και τιμή `<το-username-σου>.github.io`
   - `A` με όνομα `@` και τιμές `185.199.108.153`, `185.199.109.153`, `185.199.110.153`, `185.199.111.153`
4. Όταν περάσει ο έλεγχος (μπορεί να πάρει έως μερικές ώρες), τσέκαρε **Enforce HTTPS**.

## 5. Αλλαγή ονόματος

Το όνομα «GoalStats» υπάρχει σε δύο σημεία στο `index.html`: στο `<title>` και στο `<p class="brand">`. Άλλαξέ τα από το GitHub (κουμπί ✏️ στο αρχείο).

## Πριν το προωθήσεις

- Έλεγξε τους όρους χρήσης του football-data.co.uk, ειδικά αν βάλεις συνδρομή ή διαφημίσεις.
- Το site δείχνει αποδόσεις: έλεγξε τους κανόνες στην Κύπρο για περιεχόμενο σχετικό με στοίχημα, ειδικά πριν βάλεις links σε στοιχηματικές εταιρείες.
