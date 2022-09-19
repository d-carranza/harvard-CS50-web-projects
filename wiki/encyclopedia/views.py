from django import forms
from django.http import HttpResponseRedirect
from django.shortcuts import render
from . import util

import markdown2
import random
print(random.choice([1, 2, 3]))




class Search(forms.Form):
    query = forms.CharField(
        label="", 
        widget=forms.TextInput(attrs={
            'placeholder': 'Search a Page'
        }))

class NewPage(forms.Form):
    title = forms.CharField(label="Title")
    content = forms.CharField(label="Content", widget=forms.Textarea())

class EditPage(forms.Form):
    content = forms.CharField(label="EditContent", widget=forms.Textarea())

def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries(),
        "searchform": Search()
    })

# 1,2 - Entry pages
def entry(request, entry):
    page = util.get_entry(entry)

    if page == None:
        return render (request, "encyclopedia/404.html", {
        "entry": entry,         
        "searchform": Search()
        })
    htmlpage = markdown2.markdown(page)
    return render (
        request, "encyclopedia/entry.html", {
            "entry": entry,
            "htmlpage": htmlpage,
            "searchform": Search()
    })

# 3 - Search
def search(request):

    matches = []
    entries = util.list_entries()
    form = Search(request.GET)
    if form.is_valid():
        query = form.cleaned_data["query"]

    for entry in entries:
        # If matches, redirect
        if query in entries:
            entry = query
            return HttpResponseRedirect(f"/wiki/{entry}/")

        # If contains, add to the list (This is case sensitive so be careful)
        if query in entry:
            matches.append(entry)

    # Show list of matches
    return render(request, "encyclopedia/search.html", {
        "matches": matches,
        "searchform": Search()
    })

# 4 - Create New Page
def new(request):

    if request.method == "POST":
        form = NewPage(request.POST)
        if form.is_valid():
            title = form.cleaned_data["title"]
            content = form.cleaned_data["content"]
            if title in util.list_entries():
                return render (request, "encyclopedia/error.html", {       
                "searchform": Search()
                })
            util.save_entry(title, content)
            return HttpResponseRedirect(f"/wiki/{title}/")

    return render(request, "encyclopedia/new.html", {
        "newpageform": NewPage(),
        "searchform": Search()
})

# 5 - Edit Page
def edit(request, entry):
    page = util.get_entry(entry)
    htmlpage = markdown2.markdown(page)

    if request.method == "POST":
        print(type(page))
        form = EditPage(request.POST)
        print(form)
        print(form.is_valid())
        if form.is_valid():
            title = entry
            content = form.cleaned_data["content"]
            print(content)
            util.save_entry(title, content)
            return HttpResponseRedirect(f"/wiki/{entry}/")

    return render (
    request, "encyclopedia/edit.html", {
        "entry": entry,
        "page": page,
        "htmlpage": htmlpage,
        "editpageform": EditPage(initial={'content': page}),
        "searchform": Search()
    })

# 6 - Random
def randompage(request):

    ranpage = random.choices(util.list_entries())[0]
    return HttpResponseRedirect(f"/wiki/{ranpage}/")