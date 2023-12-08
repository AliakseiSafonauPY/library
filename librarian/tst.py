def dispatch(self, request, *args, **kwargs):
        if request.method == 'POST':
            response = None
            context = self.get_context_data(**kwargs)
            if request.POST.get('register'):
                reader = Reader.objects.get(id=self.request.GET.get('reader'))

                price_per_day = [float(request.POST[string]) for string in list(request.POST) if
                                 re.match(r'price_per_day', string) and request.POST[string]]
                act_issuing = ActIssuing.objects.get(num=context['reader'].active_act_issuing)
                copies = act_issuing.copies.all()
                issuing_date = act_issuing.issuing_date
                time = request.POST.get('time')
                time = time.split('-')
                time = date(int(time[0]), int(time[1]), int(time[2]))
                time = time - issuing_date
                time = time.days
                tentative_cost = sum([float(copies[copy].price_per_day) for copy in range(len(copies))]) * time * get_discount(len(copies))
                fine = sum([float(request.POST[string]) for string in list(request.POST) if
                            re.match(r'fine', string) and request.POST[string]])
                cost = float(tentative_cost) + fine

                if request.POST['cost']:
                    if float(request.POST['cost']) > cost:
                        cost = float(request.POST['cost'])

                act = ActReturning(num=request.POST['register'],
                                   return_date=request.POST.get('time'),
                                   cost=cost,
                                   reader=reader)
                act.save()

                for copy in copies:
                    act.copies.add(copy)
                    act.save()

                boolean = [(request.POST[string]) for string in list(request.POST) if re.match(r'status', string)]

                tre = [{re.findall('(\d+)', string)[0]: request.POST[string]} for string in list(request.POST) if
                       re.match(r'rating', string)]
                ls = [int(list(lst.keys())[0]) for lst in tre]
                books = Book.objects.filter(pk__in=ls)
                for book in range(len(books)):
                    if list(tre[book].values())[0]:
                        v = Votes(book=books[book], vote=int(list(tre[book].values())[0]))
                        v.save()

                violations = {list(x)[0]: x[list(x)[0]] for x in
                              [{re.findall('(\d+)', string)[0]: request.POST[string]} for string in list(request.POST)
                               if re.match(r'violation', string)] if x[list(x)[0]]}

                images = [{re.findall('(\d+)', string)[0]: request.FILES[string]} for string in list(request.FILES)
                          if re.match(r'img', string)]

                image = {list(images[x])[0]: [y[list(y)[0]] for y in images if list(images[x])[0] == list(y)[0]] for x
                         in range(len(images))}

                for cop in range(len(copies)):
                    copies[cop].price_per_day = price_per_day[cop]
                    if boolean[cop] == 'True':
                        copies[cop].status = True
                    elif boolean[cop] == 'False':
                        copies[cop].status = False
                    copies[cop].save()
                    if violations.get(str(copies[cop].pk)):
                        vio = Violation(copy=copies[cop],
                                        text=violations.get(str(copies[cop].pk)),
                                        act_returning=act)
                        vio.save()
                        for img in image:
                            if img.get(str(copies[cop].pk)):
                                for loky in img.get(str(copies[cop].pk)):
                                    vio_ph = ViolationPhoto(photo=loky,
                                                            violation=vio)
                                    vio_ph.save()
                response = HttpResponseRedirect(act.get_absolute_url())

            if response:
                return response
            else:
                return self.render_to_response(context)
        return super().dispatch(request, *args, **kwargs)