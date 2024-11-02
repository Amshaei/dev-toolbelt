import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog
from datetime import date
import yaml
import json
from pathlib import Path
import re

class ModernToolbeltGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Toolbelt Manager")
        self.root.geometry("1000x800")

        # Initialize cache
        self.cache = {
            'primary_category': set(),
            'secondary_category': set(),
            'language': set(),
            'proficiency': {'beginner', 'intermediate', 'advanced'},  # Default values
            'tags': set()
        }

        # Configure the style
        self.style = ttk.Style()
        self.style.configure('Header.TLabel', font=('Helvetica', 12, 'bold'))
        self.style.configure('Title.TLabel', font=('Helvetica', 16, 'bold'))
        self.style.configure('Modern.TFrame', background='#f0f0f0')
        self.style.configure('Card.TFrame', background='white', relief='solid')

        # Configure root background
        self.root.configure(bg='#f0f0f0')

        # Create main container
        self.main_container = ttk.Frame(root, style='Modern.TFrame')
        self.main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Add title
        title_frame = ttk.Frame(self.main_container, style='Modern.TFrame')
        title_frame.pack(fill='x', pady=(0, 20))
        ttk.Label(title_frame, text="Developer Toolbelt Manager",
                 style='Title.TLabel', background='#f0f0f0').pack(side='left')

        # Create content area with cards
        self.create_file_selector_card()
        self.create_form_card()

    def load_cache_from_file(self, file_path):
        """Load cached values from the YAML front matter of the file"""
        try:
            with open(file_path, 'r') as f:
                content = f.read()

            # Look for YAML front matter between --- markers
            yaml_match = re.search(r'^---\s*\n(.*?)\n---', content, re.DOTALL)
            if yaml_match:
                yaml_content = yaml_match.group(1)
                try:
                    front_matter = yaml.safe_load(yaml_content)
                    if front_matter and isinstance(front_matter, dict):
                        cache_data = front_matter.get('cache', {})

                        # Update cache with any existing values
                        for key in self.cache:
                            if key in cache_data:
                                self.cache[key].update(cache_data[key])
                except yaml.YAMLError:
                    pass

                # Extract values from existing entries
                entries = re.finditer(r'```yaml\s*---\s*\n(.*?)\n---', content, re.DOTALL)
                for entry in entries:
                    try:
                        entry_data = yaml.safe_load(entry.group(1))
                        if entry_data:
                            # Update categories
                            if 'category' in entry_data:
                                for cat in entry_data['category']:
                                    if 'primary' in cat:
                                        self.cache['primary_category'].add(cat['primary'])
                                    if 'secondary' in cat:
                                        self.cache['secondary_category'].add(cat['secondary'])

                            # Update language
                            if 'language' in entry_data:
                                self.cache['language'].add(entry_data['language'])

                            # Update tags
                            if 'tags' in entry_data:
                                self.cache['tags'].update(entry_data['tags'])
                    except yaml.YAMLError:
                        continue

            # Update all comboboxes with cached values
            self.update_comboboxes()

        except Exception as e:
            messagebox.showwarning("Cache Loading", f"Could not load cached values: {str(e)}")

    def save_cache_to_file(self, file_path):
        """Save cached values to the YAML front matter of the file"""
        try:
            # Read existing content
            content = ""
            if Path(file_path).exists():
                with open(file_path, 'r') as f:
                    content = f.read()

            # Prepare cache data for saving
            cache_data = {
                'cache': {
                    key: list(sorted(values)) for key, values in self.cache.items()
                }
            }

            yaml_content = yaml.dump(cache_data, sort_keys=False, allow_unicode=True)

            # If there's existing front matter, replace it
            if re.match(r'^---\s*\n.*?\n---', content, re.DOTALL):
                new_content = re.sub(r'^---\s*\n.*?\n---', f'---\n{yaml_content}---', content, 1, re.DOTALL)
            else:
                # If no front matter exists, add it at the top
                new_content = f'---\n{yaml_content}---\n\n{content}'

            # Write back to file
            with open(file_path, 'w') as f:
                f.write(new_content)

        except Exception as e:
            messagebox.showwarning("Cache Saving", f"Could not save cached values: {str(e)}")

    def update_comboboxes(self):
        """Update all comboboxes with current cached values"""
        if hasattr(self, 'primary_category'):
            self.primary_category['values'] = sorted(self.cache['primary_category'])
        if hasattr(self, 'secondary_category_combo'):
            self.secondary_category_combo['values'] = sorted(self.cache['secondary_category'])
        if hasattr(self, 'language_combo'):
            self.language_combo['values'] = sorted(self.cache['language'])
        if hasattr(self, 'proficiency'):
            self.proficiency['values'] = sorted(self.cache['proficiency'])

    def create_card(self, title):
        """Helper method to create a consistent card layout"""
        card = ttk.Frame(self.main_container, style='Card.TFrame')
        card.pack(fill='x', pady=(0, 20), padx=2)

        # Add inner padding
        inner_frame = ttk.Frame(card)
        inner_frame.pack(fill='x', padx=20, pady=20)

        if title:
            ttk.Label(inner_frame, text=title, style='Header.TLabel').pack(anchor='w', pady=(0, 10))

        return inner_frame

    def create_file_selector_card(self):
        card_frame = self.create_card("Catalog File Location")

        # File selection container
        file_frame = ttk.Frame(card_frame)
        file_frame.pack(fill='x')

        # File path entry
        self.file_path = ttk.Entry(file_frame, width=50, font=('Helvetica', 10))
        self.file_path.pack(side='left', padx=(0, 10))

        # Button container
        button_frame = ttk.Frame(file_frame)
        button_frame.pack(side='left')

        # Browse button
        browse_btn = ttk.Button(button_frame, text="Browse", command=self.browse_file)
        browse_btn.pack(side='left', padx=(0, 10))

        # New Toolbelt button
        new_toolbelt_btn = ttk.Button(button_frame, text="Create New Toolbelt",
                                    command=self.create_new_toolbelt)
        new_toolbelt_btn.pack(side='left', padx=(0, 10))

        # Status indicator
        self.status_label = ttk.Label(file_frame, text="❌", font=('Helvetica', 12))
        self.status_label.pack(side='left')

        # Bind file path changes to status check
        self.file_path.bind('<KeyRelease>', self.check_file_status)

    def create_form_card(self):
        form_frame = self.create_card("Tool Information")

        # Create two-column layout
        left_column = ttk.Frame(form_frame)
        left_column.pack(side='left', fill='both', expand=True, padx=(0, 10))

        right_column = ttk.Frame(form_frame)
        right_column.pack(side='left', fill='both', expand=True, padx=(10, 0))

        # Left column fields
        self.create_field(left_column, "Tool Name", "entry")
        self.create_field(left_column, "Primary Category", "combobox", cached=True)
        self.create_field(left_column, "Secondary Category", "combobox", cached=True)
        self.create_field(left_column, "Language", "combobox", cached=True)
        self.create_field(left_column, "Proficiency", "combobox", cached=True,
                         values=sorted(self.cache['proficiency']))

        # Right column fields
        self.create_field(right_column, "Documentation Links", "text",
                         placeholder="title=url, one per line")
        self.create_field(right_column, "Alternatives", "text",
                         placeholder="name=url, one per line")
        self.create_field(right_column, "Tags", "combobox", cached=True,
                         placeholder="comma-separated tags")
        self.create_field(right_column, "Description", "text")

        # Add Tool button
        btn_frame = ttk.Frame(form_frame)
        btn_frame.pack(fill='x', pady=(20, 0))
        ttk.Button(btn_frame, text="Add Tool", command=self.add_tool).pack(side='right')

    def create_field(self, parent, label, field_type, **kwargs):
        """Helper method to create consistent form fields"""
        frame = ttk.Frame(parent)
        frame.pack(fill='x', pady=(0, 15))

        ttk.Label(frame, text=label + ":", style='Header.TLabel').pack(anchor='w')

        if field_type == "entry":
            field = ttk.Entry(frame, width=40, font=('Helvetica', 10))
            field.pack(fill='x', pady=(5, 0))
            setattr(self, f"{label.lower().replace(' ', '_')}_entry", field)

        elif field_type == "combobox":
            field = ttk.Combobox(frame, width=37, font=('Helvetica', 10))
            field_name = label.lower().replace(' ', '_')

            if kwargs.get('cached', False):
                if kwargs.get('values'):
                    field['values'] = kwargs['values']
                field.bind('<Return>', lambda e, fn=field_name: self.add_to_cache(e, fn))

                # Ensure consistent naming for primary category
                if field_name == "primary_category":
                    setattr(self, "primary_category_combo", field)
                else:
                    if 'combo' not in field_name:
                        field_name += '_combo'
                    setattr(self, field_name, field)
            else:
                field['values'] = kwargs.get('values', [])
                setattr(self, field_name, field)
            field.pack(fill='x', pady=(5, 0))

        elif field_type == "text":
            field = scrolledtext.ScrolledText(frame, width=35, height=4, font=('Helvetica', 10))
            field.pack(fill='x', pady=(5, 0))
            if 'placeholder' in kwargs:
                field.insert('1.0', kwargs['placeholder'])
                field.bind('<FocusIn>', lambda e: self.clear_placeholder(field, kwargs['placeholder']))
                field.bind('<FocusOut>', lambda e: self.restore_placeholder(field, kwargs['placeholder']))
            setattr(self, f"{label.lower().replace(' ', '_')}_text", field)


    def add_to_cache(self, event, field_name):
        """Add new value to cache and update comboboxes"""
        widget = getattr(self, field_name if not field_name.endswith('_combo') else field_name[:-6])
        value = widget.get().strip()

        if value:
            self.cache[field_name].add(value)
            self.update_comboboxes()

            # Save cache to file if file path exists
            if self.file_path.get():
                self.save_cache_to_file(self.file_path.get())

    def clear_placeholder(self, widget, placeholder):
        if widget.get('1.0', 'end-1c') == placeholder:
            widget.delete('1.0', tk.END)

    def restore_placeholder(self, widget, placeholder):
        if not widget.get('1.0', 'end-1c').strip():
            widget.delete('1.0', tk.END)
            widget.insert('1.0', placeholder)

    def browse_file(self):
        initial_dir = Path.home()
        filename = filedialog.asksaveasfilename(
            initialdir=initial_dir,
            title="Select Catalog File",
            filetypes=(("Markdown files", "*.md"), ("All files", "*.*")),
            defaultextension=".md"
        )
        if filename:
            self.file_path.delete(0, tk.END)
            self.file_path.insert(0, filename)
            self.check_file_status()

            # Load cache if file exists
            if Path(filename).exists():
                self.load_cache_from_file(filename)

    def check_file_status(self, event=None):
        file_path = self.file_path.get()
        if file_path:
            path = Path(file_path)
            if path.exists():
                self.status_label.config(text="✓")
                self.load_cache_from_file(file_path)
            elif path.parent.exists():
                self.status_label.config(text="✓")
            else:
                self.status_label.config(text="❌")
        else:
            self.status_label.config(text="❌")

    def parse_link_text(self, text, split_char='='):
        items = []
        for line in text.strip().split('\n'):
            if line.strip():
                try:
                    title, url = line.split(split_char, 1)
                    items.append({
                        "title": title.strip(),
                        "url": url.strip()
                    })
                except ValueError:
                    continue
        return items

    # Update the add_tool method to use correct attribute names
    def add_tool(self):
        if not self.file_path.get():
            messagebox.showerror("Error", "Please select a catalog file location first!")
            return

        # Gather all the data
        tool_data = {
            "name": self.tool_name_entry.get(),
            "category": [
                {
                    "primary": self.primary_category_combo.get(),
                    "secondary": self.secondary_category_combo.get()
                }
            ],
            "language": self.language_combo.get(),
            "lastUsed": date.today().isoformat(),
            "proficiency": self.proficiency_combo.get(),
            "documentation": self.parse_link_text(self.documentation_links_text.get("1.0", tk.END)),
            "alternatives": self.parse_link_text(self.alternatives_text.get("1.0", tk.END)),
            "tags": [tag.strip() for tag in self.tags_combo.get().split(",") if tag.strip()],
            "description": self.description_text.get("1.0", tk.END).strip()
        }
        # Create the markdown
        markdown_entry = f"""### {tool_data['name']}

```yaml
---
{yaml.dump(tool_data, sort_keys=False, allow_unicode=True)}
---
```

"""
        # Update cache with new values
        if tool_data['category'][0]['primary']:
            self.cache['primary_category'].add(tool_data['category'][0]['primary'])
        if tool_data['category'][0]['secondary']:
            self.cache['secondary_category'].add(tool_data['category'][0]['secondary'])
        if tool_data['language']:
            self.cache['language'].add(tool_data['language'])
        self.cache['tags'].update(tool_data['tags'])

        # Save cache and append tool entry
        try:
            # Save updated cache to file
            self.save_cache_to_file(self.file_path.get())

            # Append new tool entry
            with open(self.file_path.get(), "a") as f:
                f.write("\n" + markdown_entry)

            # Update comboboxes with new values
            self.update_comboboxes()

            messagebox.showinfo("Success", f"Added {tool_data['name']} to catalog!")
            self.clear_form()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add tool: {str(e)}")

    def clear_form(self):
        """Clear all form fields but maintain cached values in dropdowns"""
        self.tool_name_entry.delete(0, tk.END)
        self.primary_category.set('')
        self.secondary_category_combo.set('')
        self.language_combo.set('')
        self.proficiency.set('')
        self.documentation_links_text.delete("1.0", tk.END)
        self.documentation_links_text.insert("1.0", "title=url, one per line")
        self.alternatives_text.delete("1.0", tk.END)
        self.alternatives_text.insert("1.0", "name=url, one per line")
        self.tags_combo.set('')
        self.description_text.delete("1.0", tk.END)

    def clear_form(self):
        """Clear all form fields but maintain cached values in dropdowns"""
        self.tool_name_entry.delete(0, tk.END)
        self.primary_category.set('')
        self.secondary_category_combo.set('')
        self.language_combo.set('')
        self.proficiency.set('')
        self.documentation_links_text.delete("1.0", tk.END)
        self.documentation_links_text.insert("1.0", "title=url, one per line")
        self.alternatives_text.delete("1.0", tk.END)
        self.alternatives_text.insert("1.0", "name=url, one per line")
        self.tags_combo.set('')
        self.description_text.delete("1.0", tk.END)

    def create_new_toolbelt(self):
        """Create a new toolbelt markdown file with proper template"""
        initial_dir = Path.home()
        filename = filedialog.asksaveasfilename(
            initialdir=initial_dir,
            title="Create New Toolbelt File",
            filetypes=(("Markdown files", "*.md"),),
            defaultextension=".md"
        )
        if filename:
            template = """---
cache:
primary_category: []
secondary_category: []
language: []
proficiency: ['beginner', 'intermediate', 'advanced']
tags: []
---
# Developer's Toolbelt
This file contains a curated list of development tools and resources.

## Tool Template (YAML)

```yaml
---
name: Tool Name
category:
  - primary: "Development Tools"
  - secondary: "Template"
language: YAML
lastUsed: YYYY-MM-DD
proficiency: beginner|intermediate|advanced
documentation:
  - title: "Official Documentation"
    url: "https://example.com/docs"
  - title: "NPM Package"
    url: "https://www.npmjs.com/package/example"
alternatives:
  - name: "Alternative Tool"
    url: "https://example.com"
tags:
  - example
  - template
---

"""
            try:
                with open(filename, 'w') as f:
                    f.write(template)
                # Fix: Use delete and insert instead of set
                self.file_path.delete(0, tk.END)
                self.file_path.insert(0, filename)
                messagebox.showinfo("Success", "Created new toolbelt file!")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to create file: {str(e)}")


if __name__ == "__main__":
    root = tk.Tk()
    app = ModernToolbeltGUI(root)
    root.mainloop()
