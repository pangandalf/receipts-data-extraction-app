import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk, ExifTags
import receipt_processing as rp
import ocr_to_json as otj

from ocr_to_json import append_receipt_to_db, get_receipts, create_receipt, parse_receipt

class ReceiptApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Receipt Manager")
        self.geometry("860x750")

        self.tab_control = ttk.Notebook(self)
        self.add_receipt_tab = ttk.Frame(self.tab_control)
        self.tab_control.add(self.add_receipt_tab, text="Dodaj Paragon")

        self.view_receipts_tab = ttk.Frame(self.tab_control)
        self.tab_control.add(self.view_receipts_tab, text="Przeglądaj Paragony")

        self.statistics_tab = ttk.Frame(self.tab_control)
        self.tab_control.add(self.statistics_tab, text="Statystyki")

        self.tab_control.pack(expand=True, fill=tk.BOTH)

        self.setup_add_receipt_tab()
        self.setup_view_receipts_tab()
        self.setup_statistics_tab()


    def setup_add_receipt_tab(self):
        self.add_receipt_frame = ttk.Frame(self.add_receipt_tab)
        self.add_receipt_frame.pack(expand=True, fill=tk.BOTH)

        self.left_frame = ttk.Frame(self.add_receipt_frame)
        self.left_frame.pack(side=tk.LEFT, fill=tk.Y)

        self.right_frame = ttk.Frame(self.add_receipt_frame)
        self.right_frame.pack(side=tk.RIGHT, expand=True, fill=tk.BOTH)

        # image in the left frame
        self.image_label = tk.Label(self.left_frame)
        self.image_label.pack()

        self.info_frame = ttk.Frame(self.right_frame)
        self.info_frame.pack(pady=10, fill=tk.BOTH, expand=True)

        self.store_name_label = ttk.Label(self.info_frame, text="Nazwa sklepu:")
        self.store_name_entry = ttk.Entry(self.info_frame, width=40)

        self.date_label = ttk.Label(self.info_frame, text="Data dodania paragonu:")
        self.date_entry = ttk.Entry(self.info_frame, width=40)

        self.upload_button = ttk.Button(self.info_frame, text="Wybierz zdjęcie", command=self.upload_image)
        self.upload_button.pack(pady=10)

        self.products_frame = ttk.Frame(self.info_frame)

        self.add_receipt_button = ttk.Button(self.info_frame, text="Dodaj Paragon", command=self.add_receipt)

        self.total_sum_label = ttk.Label(self.info_frame, text="Suma PLN:")
        self.total_sum_entry = ttk.Entry(self.info_frame, width=40)

        self.product_entries = []  # list for products

    def update_product_entries(self):
        # clear products fields
        for widget in self.products_frame.winfo_children():
            widget.destroy()

        self.product_entries = []

        # adding column names
        headers_frame = ttk.Frame(self.products_frame)
        headers_frame.grid(row=0, columnspan=5, pady=5)

        ttk.Label(headers_frame, text="                               ").grid(row=0, column=0, padx=5, pady=5)
        ttk.Label(headers_frame, text=" Ilość").grid(row=0, column=1, padx=5, pady=5)
        ttk.Label(headers_frame, text="    Cena 1szt.").grid(row=0, column=2, padx=5, pady=5)
        ttk.Label(headers_frame, text="    Cena").grid(row=0, column=3, padx=5, pady=5)
        ttk.Label(headers_frame, text="             Rabat").grid(row=0, column=4, padx=5, pady=5)

        # fields for products
        for idx, product in enumerate(self.data):
            row_index = idx + 1

            product_amount = int(product[1]) if product[1].is_integer() else product[1]

            product_name_entry = ttk.Entry(self.products_frame, width=20)
            product_name_entry.insert(0, product[0])

            product_amount_entry = ttk.Entry(self.products_frame, width=5)
            product_amount_entry.insert(0, str(product_amount))

            product_unit_price_entry = ttk.Entry(self.products_frame, width=10)
            product_unit_price_entry.insert(0, "{:.2f}".format(product[2]))

            product_total_price_entry = ttk.Entry(self.products_frame, width=10)
            product_total_price_entry.insert(0, "{:.2f}".format(product[3]))

            product_discount_entry = ttk.Entry(self.products_frame, width=10)
            product_discount_entry.insert(0, "{:.2f}".format(product[4]))

            product_name_entry.grid(row=row_index, column=0, padx=5, pady=5)
            product_amount_entry.grid(row=row_index, column=1, padx=5, pady=5)
            product_unit_price_entry.grid(row=row_index, column=2, padx=5, pady=5)
            product_total_price_entry.grid(row=row_index, column=3, padx=5, pady=5)
            product_discount_entry.grid(row=row_index, column=4, padx=5, pady=5)

            self.product_entries.append((product_name_entry, product_amount_entry, product_unit_price_entry, product_total_price_entry, product_discount_entry))

    def correct_image_orientation(self, image):
        try:
            for orientation in ExifTags.TAGS.keys():
                if ExifTags.TAGS[orientation] == 'Orientation':
                    break

            exif = dict(image._getexif().items())
            orientation = exif.get(orientation, None)

            if orientation == 3:
                image = image.rotate(180, expand=True)
            elif orientation == 6:
                image = image.rotate(270, expand=True)
            elif orientation == 8:
                image = image.rotate(90, expand=True)

        except Exception as e:
            print("Problem z korekcją orientacji:", e)

        return image

    def upload_image(self):
        filename = filedialog.askopenfilename(
            title="Wybierz zdjęcie paragonu",
            filetypes=[("Pliki graficzne", "*.jpg;*.jpeg;*.png")]
        )

        if filename:
            try:
                # data extraction from receipt
                store_name, date, self.data = rp.receipt_extraction(filename)
                total_sum = otj.suma_rabatow(self.data)

                # showing image in UI
                image = Image.open(filename)
                image = self.correct_image_orientation(image)
                image = image.resize((440, 720), Image.Resampling.LANCZOS)
                image_tk = ImageTk.PhotoImage(image)

                self.image_label.configure(image=image_tk)
                self.image_label.image = image_tk

                self.store_name_label.pack()  # visible after adding image
                self.store_name_entry.pack()
                self.store_name_entry.delete(0, tk.END)
                self.store_name_entry.insert(0, store_name)

                self.date_label.pack()  # visible after adding image
                self.date_entry.pack()
                self.date_entry.delete(0, tk.END)
                self.date_entry.insert(0, date)

                self.products_frame.pack(pady=10, fill=tk.BOTH, expand=True)
                self.update_product_entries()  # fields with edit option

                self.total_sum_label.pack()
                self.total_sum_entry.pack()
                self.total_sum_entry.delete(0, tk.END)
                self.total_sum_entry.insert(0, str(round(total_sum, 2)))

                self.add_receipt_button.pack(pady=10)
            except Exception as e:
                messagebox.showerror("Błąd", f"Wystąpił problem z przetwarzaniem obrazu: {e}")

    def add_receipt(self):
        try:
            store_name = self.store_name_entry.get()
            date = self.date_entry.get()
            total_sum = float(self.total_sum_entry.get())

            updated_products = []
            for krotka in self.product_entries:
                product_name = krotka[0].get()
                product_amount = float(krotka[1].get())
                product_unit_price = float(krotka[2].get())
                product_total_price = float(krotka[3].get())
                product_discount = float(krotka[4].get())

                updated_products.append([product_name, product_amount, product_unit_price, product_total_price, product_discount])

            receipt = otj.create_receipt(store_name, date, updated_products, total_sum)

            otj.append_receipt_to_db(receipt)

            # showing receipt details after succesful saving to db file
            product_lines = "\n".join([f"{prod[0]}: {prod[1]} x {prod[2]} = {prod[3]}" for prod in updated_products])
            receipt_details = f"Sklep: {store_name}\nData: {date}\nSuma: {round(total_sum, 2)}\n\nProdukty:\n{product_lines}"

            messagebox.showinfo("Sukces", receipt_details)
        except Exception as e:
            messagebox.showerror("Błąd", f"Nie udało się dodać paragonu: {e}")

    def setup_view_receipts_tab(self):
        MAIN_FRAME_HEIGHT = 0.8
        self.main_frame = ttk.Frame(self.view_receipts_tab)
        self.main_frame.pack(expand=True, fill=tk.BOTH)

        self.list_frame = ttk.Frame(self.main_frame, height=MAIN_FRAME_HEIGHT * 750)  # 4/5 z 750
        self.list_frame.pack(side=tk.LEFT, fill=tk.Y, expand=True)

        self.details_frame = ttk.Frame(self.main_frame, height=MAIN_FRAME_HEIGHT * 750)
        self.details_frame.pack(side=tk.RIGHT, fill=tk.Y, expand=True)

        self.receipts_listbox = tk.Listbox(self.list_frame, width=40, height=40)
        self.receipts_listbox.pack(pady=10)

        self.refresh_button = ttk.Button(self.list_frame, text="Odśwież", command=self.refresh_receipts)
        self.refresh_button.pack(pady=10)

        self.receipt_details = tk.Text(self.details_frame, wrap=tk.WORD, height=40, width=60)
        self.receipt_details.pack(pady=10)

        self.receipts_listbox.bind("<<ListboxSelect>>", self.show_receipt_details)

        self.refresh_receipts()  # refresh after start of the app

    def refresh_receipts(self):
        self.receipts_listbox.delete(0, tk.END)

        try:
            receipts = otj.get_receipts()
            if not receipts:
                raise Exception("Lista paragonów jest pusta")

            for idx, receipt in enumerate(receipts):
                if isinstance(receipt, str):
                    store_name, date, products, total_price = parse_receipt(receipt)

                    receipt_info = f"Sklep: {store_name}, Data: {date}, Suma: {total_price}"
                    self.receipts_listbox.insert(tk.END, receipt_info)

        except Exception as e:
            messagebox.showerror("Błąd", f"Nie udało się odświeżyć listy paragonów: {e}")

    def show_receipt_details(self, event):
        selection = event.widget.curselection()  # index of selected receipt
        if not selection:
            print("Nie wybrano żadnego paragonu.")
            return

        idx = selection[0]

        try:
            receipts = otj.get_receipts()
            if not receipts or idx >= len(receipts):
                raise Exception("Indeks poza zakresem lub lista paragonów jest pusta.")

            selected_receipt_json = receipts[idx]

            store_name, date, products, total_price = parse_receipt(selected_receipt_json)

            self.receipt_details.delete(1.0, tk.END)  # clearing text

            name_width = 30

            product_lines = "\n".join(
                [f"{prod['name'].ljust(name_width)} {prod['amount']} x {prod['price']} = {prod['total']}" for prod in products]
            )

            receipt_details = (
                f"Sklep: {store_name}\nData: {date}\nSuma: {round(total_price, 2)}\n\nProdukty:\n{product_lines}"
            )

            self.receipt_details.insert(tk.END, receipt_details)  # displaying formatted text

        except Exception as e:
            messagebox.showerror("Błąd", f"Nie udało się wyświetlić szczegółów paragonu: {e}")

    def setup_statistics_tab(self):
        self.sort_options = ttk.Combobox(
            self.statistics_tab,
            values=[
                "Sortuj według sklepu",
                "Sortuj po cenie rosnąco",
                "Sortuj po cenie malejąco",
            ],
            state="readonly",
        )
        self.sort_options.current(0)
        self.sort_options.bind("<<ComboboxSelected>>", self.handle_sort_selection)
        self.sort_options.pack(pady=10)

        self.stats_display = tk.Text(self.statistics_tab, wrap=tk.WORD, height=25, width=80)
        self.stats_display.pack(pady=10, fill=tk.BOTH, expand=True)

    def handle_sort_selection(self, event):
        selected_sort = self.sort_options.get()
        if selected_sort == "Sortuj według sklepu":
            self.sort_by_store()
        elif selected_sort == "Sortuj po cenie rosnąco":
            self.sort_products("ascending")
        elif selected_sort == "Sortuj po cenie malejąco":
            self.sort_products("descending")

    def sort_by_store(self):
        try:
            receipts = otj.get_receipts()
            if not receipts:
                raise Exception("Brak paragonów w bazie danych.")

            store_stats = {}

            for receipt in receipts:
                store_name, _, products, total = otj.parse_receipt(receipt)

                if store_name not in store_stats:
                    store_stats[store_name] = {"count": 0, "total": 0.0}

                store_stats[store_name]["count"] += 1
                store_stats[store_name]["total"] += total

            # sort by spendings amount
            sorted_store_stats = sorted(
                store_stats.items(), key=lambda x: x[1]["total"], reverse=True
            )

            self.stats_display.delete(1.0, tk.END)  # clear the field
            for store, stats in sorted_store_stats:
                self.stats_display.insert(
                    tk.END,
                    f"{store}\n"
                    f"Liczba paragonów: {int(stats['count'])}\n" 
                    f"Łączna wydana kwota: {stats['total']:.2f}\n\n",
                )

        except Exception as e:
            messagebox.showerror("Błąd", f"Nie udało się pobrać statystyk: {e}")

    def sort_products(self, direction):
        try:
            receipts = otj.get_receipts()
            if not receipts:
                raise Exception("Brak paragonów w bazie danych.")

            product_stats = {}

            for receipt in receipts:
                _, _, products, _ = otj.parse_receipt(receipt)

                for product in products:
                    product_name = product.get("name", "")

                    if product_name not in product_stats:
                        product_stats[product_name] = {"count": 0, "total": 0.0}

                    product_stats[product_name]["count"] += product["amount"]
                    product_stats[product_name]["total"] += product["total"]

            sorted_product_stats = sorted(
                product_stats.items(),
                key=lambda x: x[1]["total"],
                reverse=(direction == "descending"),
            )

            self.stats_display.delete(1.0, tk.END)
            name_width = 40
            for product_name, stats in sorted_product_stats:
                amount_str = (
                    str(int(stats["count"])) if stats["count"] % 1 == 0 else str(stats["count"])
                )

                product_info = (
                    product_name.ljust(name_width)
                    + amount_str.rjust(10)
                    + f"{stats['total']:.2f}".rjust(15)
                    + "\n"
                )

                self.stats_display.insert(tk.END, product_info)
        except Exception as e:
            messagebox.showerror("Błąd", f"Nie udało się pobrać statystyk: {e}")

if __name__ == "__main__":
    app = ReceiptApp()
    app.mainloop()