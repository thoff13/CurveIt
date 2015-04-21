from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, get_list_or_404, redirect
from django.contrib.auth.decorators import login_required
from curves.models import Course_Specific, Student
from curves.forms import Course_SpecificForm
from deptscript import depts
import json

CURRENTSEMESTER = "S2015"
GRADES = ["A+", "A", "A-", "B+", "B", "B-", "C+", "C", "C-", "D_grade", "F_grade"]

# Create your views here.
@login_required

def index(request):
    #code here that goes through all the course-specifics and generates three lists of strings,
    #profs, depts, and courses, and we then pass this on as context to index.html.
    classes = Course_Specific.objects.all()

    allProfs = []
    allProfsExact = []
    allDepts = []
    allDeptsExact = []
    allTitles = []
    allTitlesExact = []
    allCombined = []

    for c in classes:
        fields = c.printFields()
        if fields['title'] not in allTitlesExact:
            curDict = {}
            curData = {}
            curDict["value"] = fields['title']
            curData["cat"] = "Name"
            curDict["data"] = curData
            allTitles.append(curDict)
            allTitlesExact.append(fields['title'])

        for prof in fields['profs']:
            if prof not in allProfsExact:
                curDict = {}
                curData = {}
                curDict["value"] = prof
                curData["cat"] = "Professor"
                curDict["data"] = curData
                allProfs.append(curDict)
                allProfsExact.append(prof)

        for dept in fields['depts']:
            if dept not in allDeptsExact:
                curDict = {}
                curData = {}
                curDict["value"] = dept
                curData["cat"] = "Departments"
                curDict["data"] = curData
                allDepts.append(curDict)
                allDeptsExact.append(dept)

    allCombined = allDepts + allTitles + allProfs
    allCombinedJSON = json.dumps(allCombined)

    context = {'allCombinedJSON': allCombinedJSON}
    return render(request, 'curves/index.html', context)

def loggedIn(request):
    currentnetid = request.user.username
    thisUser = Student.objects.get(netid=currentnetid)
    return (thisUser.hasAccess())

def alreadyEntered(request):
    currentnetid = request.user.username
    print currentnetid
    thisUser = Student.objects.get(netid=currentnetid)
    print thisUser
    return thisUser.has_Entered

@login_required 
# ex: curves/COS.  Shows dropdown for all distinct COS classes taught since birth, 
# plot of all time aggregate distribution, links to deptSpecific for each semester.
def deptView(request, cdept):
    if loggedIn(request) == False:
        return redirect('/add_data/')
    # get all courses registered under the department, including those that are cross listed
    course_list = get_list_or_404(Course_Specific, dept__icontains = cdept) # includes all semesters
    
    # construct list of unique course titles
    uniqueCourse_list = []
    # construct a list of all semesters for which we have data
    sem_list = []
    for course in course_list:
        # get list of all distinct courses
        for uniqueCourse in uniqueCourse_list:
            if course.num == uniqueCourse.num:
                break
        else:
            uniqueCourse_list.append(course)
        # get list of all distinct semesters
        for sem in sem_list:
            if course.semester == sem:
                break
        else:
            sem_list.append(course.semester)

    # aggregate all time grade distribution
    numGrades = [0] * len(GRADES)
    for course in course_list:
        grades = course.getAllGrades()
        for i in range(0, len(grades)):
            numGrades[i] += grades[i]

    dist = zip(GRADES, numGrades)
    total = sum(numGrades)

    # sem_list sorted in reverse so that they appear in reverse chronological order
    context = {'deptForPrint': depts[cdept.upper()], 'dept': cdept.upper(), 'course_list': uniqueCourse_list, 'dist': dist, 'total': total, 'sem_list': sorted(sem_list, reverse=True)}
    return render(request, 'curves/dept.html', context)

# ex: curves/COS/S2015.  Shows plot of grade distribution for all COS classes taught
# during the given semester.
def deptSpecificView(request, cdept, ctime):
    if loggedIn(request) == False:
        return redirect('/add_data/')
    # list of all classes in the department over all semesters
    allSemAllCourse = get_list_or_404(Course_Specific, dept__contains = cdept)
    # check that the dept exists for the semester
    checkExists = get_list_or_404(Course_Specific, dept__contains = cdept, semester = ctime)

    # all courses for current semester
    course_list = []
    # all semester for which classes under this dept were taught
    sem_list = []
    # get list of all distinct semesters
    for course in allSemAllCourse:
        # create list of all the classes in the current semester
        if course.semester == ctime:
            course_list.append(course)

        # create a list of all the distinct semesters
        for sem in sem_list:
            if course.semester == sem:
                break
        else:
            sem_list.append(course.semester)

    numGrades = [0] * len(GRADES)
    for course in course_list:
        grades = course.getAllGrades()
        for i in range(0, len(grades)):
            numGrades[i] += grades[i]

    dist = zip(GRADES, numGrades)

    # departments sorted in reverse so they appear like S2015 S2014, etc...
    context = {'deptForPrint': depts[cdept], 'dept': cdept, 'course_list': course_list, 'dist': dist, 'sem': ctime, 'sem_list': sorted(sem_list, reverse=True)}
    return render(request, 'curves/dept_specific.html', context)


@login_required
# ex: curves/prof/Brian%W.%Kernighan. Plot of all time aggregate distribution, links to
# professorSpecific for each semester, dropdown of all courses taught.
def profView(request, cprof):
    if loggedIn(request) == False:
        return redirect('/add_data/')
    allSemAllCourse = get_list_or_404(Course_Specific, prof__icontains = cprof)
    print "Justin"
    sem_list = []
    course_list = []

    for c in allSemAllCourse:
        # get a list of all distinct courses
        for uniqueCourse in course_list:
            if c.num == uniqueCourse.num and c.dept == uniqueCourse.dept:
                break
        else:
            course_list.append(c)

        # get a list of all distinct semesters taught
        for sem in sem_list:
            if c.semester == sem:
                break
        else:
            sem_list.append(c.semester)

    # generate grade distibution across all courses taught
    numGrades = [0] * len(GRADES);
    for course in course_list:
        grades = course.getAllGrades()
        for i in range(0, len(grades)):
            numGrades[i] += grades[i]

    dist = zip(GRADES, numGrades)
    print cprof
    context = {'course_list': course_list, 'sem_list': sorted(sem_list, reverse=True), 'profForPrint': cprof.replace("*", " "), 'prof': cprof, 'dist': dist}
    return render(request, 'curves/prof.html', context)

# ex: curves/prof/Brian+W.+Kernighan/S2015.  Shows plot of grade distribution for all COS classes taught
# during the given semester, links to other semesters
def profSpecificView(request, cprof, ctime):
    print "Tye"
    print cprof
    if loggedIn(request) == False:
        return redirect('/add_data/')
    print "tyler is cool"
    allsemallcourse = get_list_or_404(Course_Specific, prof__icontains = cprof)
    # check that the prof data exists for the semester
    checkExists = get_list_or_404(Course_Specific, prof__icontains = cprof, semester = ctime)


    course_list = []
    sem_list = []

    for c in allsemallcourse:
        # create a list of all classes in the current semester
        if c.semester == ctime:
            course_list.append(c)

        # create a list of all semesters in which professor taught
        for sem in sem_list:
            if c.semester == sem:
                break
        else:
            sem_list.append(c.semester)

    # generate grade distribution across all coureses taught
    numGrades = [0] * len(GRADES);
    for course in course_list:
        grades = course.getAllGrades()
        for i in range(0, len(grades)):
            numGrades[i] += grades[i]

    dist = zip(GRADES, numGrades)
    context = {'course_list': course_list, 'sem_list': sorted(sem_list, reverse=True), 'profForPrint': cprof.replace("*", " "), 'prof': cprof, 'sem': ctime, 'dist': dist}
    return render(request, 'curves/prof_specific.html', context)


@login_required
# ex: curves/COS/333. Plot of all time aggregate distribution, links to 
# courseSpecific for each semester
def courseView(request, cdept, cnum):
    if loggedIn(request) == False:
        return redirect('/add_data/')
    # gets list of this course over all semesters
    course_list = get_list_or_404(Course_Specific, dept=cdept, num=cnum)


    # list of all semesters this class was taught
    sem_list = []

    # list of all professors who have taught this class
    prof_list = []
    prof_names_list = []

    numGrades = [0] * len(GRADES);
    for course in course_list:
        sem_list.append(course.semester)
        curProf = course.prof
        curProfs = curProf.split("+")
        for c in curProfs:
            for p in prof_list:
                if c == p:
                    break   
            else:
                prof_list.append(c)
        grades = course.getAllGrades()
        for i in range(0, len(grades)):
            numGrades[i] += grades[i]
    for p in prof_list:
        thisProf = p.replace("*", " ")
        prof_names_list.append(thisProf)

    print prof_names_list
    # in order to pass in name of this class
    curCourse = course_list[0]
    dist = zip(GRADES, numGrades)
    profs = zip(prof_list, prof_names_list)
    total = sum(numGrades) 
    context = {'sem_list': sorted(sem_list, reverse=True), 'profs': profs, 'dist': dist,'total': total, 'name': curCourse.__unicode__(), 'course': curCourse}
    return render(request, 'curves/course.html', context)

@login_required
# ex: curves/COS/333/S2015.  Plot of grade distribution for course taught during
# given semester.  Provide links to all other semesters for the course.  
def courseSpecificView(request, cdept, cnum, ctime):
    if loggedIn(request) == False:
        return redirect('/add_data/')
    # course specific to the semester
    course = get_object_or_404(Course_Specific, dept = cdept, num = cnum, semester = ctime)
    # course over all semesters
    course_list = get_list_or_404(Course_Specific, dept = cdept, num = cnum)    
    # all semesters for which this class was taught
    sem_list = []
    for c in course_list:
        sem_list.append(c.semester)

    numGrades = course.getAllGrades()
    dist = zip(GRADES, numGrades)
    print dist
    total = sum(numGrades)

    curProfsForPrint = []
    curProfs = []
    profs = course.prof.split("+")
    for p in profs:
        curProfs.append(p)
        curProfsForPrint.append(p.replace("*", " "))
    profs = zip(curProfs, curProfsForPrint)
    context = {'sem_list': sorted(sem_list, reverse=True), 'course': course, 'name': course.__unicode__(), 'dist': dist, 'total': total, 'profs': profs}
    # context = {'course': course, "grades": GRADES, "numGrades": numGrades}
    return render(request, 'curves/course_specific.html', context)

@login_required
# page for user to input class/grade
def add_data(request):
    if alreadyEntered(request):
        print "he;;p"
        return redirect('/')
    # A HTTP POST?
    y = range(1,4)
    z = range(4, 8)
    currentnetid = request.user.username
    requiredClasses = map(lambda x: "pastSemClass" + str(x), y)
    requiredGrades = map(lambda x: "grade" + str(x), y)
    optionalClasses = map(lambda x: "pastSemClass" + str(x), z)
    optionalGrades = map(lambda x: "grade" + str(x), z)
    if request.method == 'POST':
        form = Course_SpecificForm(request.POST)

        # Have we been provided with a valid form?
        if form.is_valid():
            thisUser = Student.objects.get(netid=currentnetid)
            thisUser.entered()
            thisUser.save()
            curData = form.cleaned_data
            try:
                for i in range(0, len(requiredClasses)):
                    c = requiredClasses[i]
                    g = requiredGrades[i]
                    thisClass = curData[c] # i.e. AAS 210/MUS 253: Intro to...
                    thisGrade = curData[g] # gets grade chosen
                    thisClass.addGrade(thisGrade)
                    thisClass.save()
                for i in range(0, len(optionalClasses)):
                    thisClass = curData[optionalClasses[i]] # i.e. AAS 210/MUS 253: Intro to...
                    if thisClass != None:
                        thisGrade = curData[optionalGrades[i]] # gets grade chosen
                        thisClass.addGrade(thisGrade)
                        thisClass.save()
                # thisClass2 = curData["pastSemClass2"] # i.e. AAS 210/MUS 253: Intro to...
                # thisGrade2 = curData["grade2"] # gets grade chosen
                # thisClass2.addGrade(thisGrade2)
                # thisClass2.save()
                # thisClass3 = curData["pastSemClass3"] # i.e. AAS 210/MUS 253: Intro to...
                # thisGrade3 = curData["grade3"] # gets grade chosen
                # thisClass3.addGrade(thisGrade3)
                # thisClass3.save()
                # thisClass4 = curData["pastSemClass4"] # i.e. AAS 210/MUS 253: Intro to...
                # if thisClass4 != None:
                #     thisGrade4 = curData["grade4"] # gets grade chosen
                #     thisClass4.addGrade(thisGrade4)
                #     thisClass4.save()
                # thisClass5 = curData["pastSemClass5"] # i.e. AAS 210/MUS 253: Intro to...
                # if thisClass5 != None:
                #     thisGrade5 = curData["grade5"] # gets grade chosen
                #     thisClass5.addGrade(thisGrade5)
                #     thisClass5.save()
                # thisClass6 = curData["pastSemClass6"] # i.e. AAS 210/MUS 253: Intro to...
                # if thisClass6 != None:
                #     thisGrade6 = curData["grade6"] # gets grade chosen
                #     thisClass6.addGrade(thisGrade6)
                #     thisClass6.save()
                # thisClass7 = curData["pastSemClass7"] # i.e. AAS 210/MUS 253: Intro to...
                # if thisClass7 != None:
                #     thisGrade7 = curData["grade7"] # gets grade chosen
                #     thisClass7.addGrade(thisGrade7)
                #     thisClass7.save()
                # thisClassInfo = thisClass.split("/") # i.e. ["AAS 210", "MUS 253: Intro to..."]
                # lastString = thisClassInfo[len(thisClassInfo)-1]
                # lastDept = (lastString)[0:lastString.index(":")] # gets department i.e. "MUS 253"
                # thisName = (lastString)[(lastString.index(":") + 2):] # gets name i.e. "Intro to...""

                # # now thisClassInfo is a list of all dist/num pairs
                # thisClassInfo = thisClassInfo[:-1] 
                # thisClassInfo.append(lastDept) # i.e. ["AAS 210", "MUS 253"]

                # # will be a list of depts in format AAS+MUS
                # depts = ""
                # # will be a list of nums 210+253
                # nums = ""

                # for i in range(0, len(thisClassInfo)):
                #     curListings = thisClassInfo[i].split()
                #     thisDept = curListings[0]
                #     thisNum = curListings[1]
                #     if i == (len(thisClassInfo) - 1):
                #         depts += thisDept
                #         nums += thisNum
                #     else:
                #         depts += thisDept + "+"
                #         nums += thisNum + "+"

                # thisClass = get_object_or_404(Course_Specific, dept=depts, num=nums, semester=CURRENTSEMESTER)

            except Course_Specific.DoesNotExist:
                thisClass = None

            # Now call the index() view.
            # The user will be shown the homepage.
            return redirect('/after_data/')
    else:
        # If the request was not a POST, display the form to enter details.
        form = Course_SpecificForm()

    # Bad form (or form details), no form supplied...
    # Render the form with error messages (if any).
    print "gagjaw"
    return render(request, 'curves/add_data.html', {'form': form})

def after_data(request):
    if loggedIn(request) == False:
        return redirect('/add_data/')
    return render(request, 'curves/after_data.html')       

def search(request):
    if loggedIn(request) == False:
        return redirect('/add_data/')
    if 'q' in request.GET and request.GET['q'] and len(request.GET['q']) > 2:
        q = request.GET['q']

        #check if search term exactly matches a Course's unicode print
        for c in Course_Specific.objects.all():
            if unicode(c) == q:
                return courseView(request, c.dept, c.num)

        #check if search term is a department?
        if len(q) == 3:
            classes = Course_Specific.objects.filter(dept__iexact=q)
            if (len(classes) > 0):
                #context = {'classes': classes}
                #return render(request, 'curves/results.html', context)
                aClass = classes[0]
                return deptView(request, aClass.dept)

        #check if the search term is part of a professor?
        qS = q.split(" ")
        classes = Course_Specific.objects.filter(prof__icontains=qS[0])
        for i in range(0, len(qS)):
            classes = classes.filter(prof__icontains=qS[i])
            #context = {'classes': classes}
            #return render(request, 'curves/results.html', context)
            #logic works temporarily, need autocomplete because currently
            #will just display view of the first found professor that matches query!
        if len(classes) > 0:
            profs = classes[0].prof.split("+")
            for p in profs:
                for s in qS:
                    if s.lower() not in p.lower():
                        break
                    else:
                        return profView(request, p)

        #check if search term is a dept/num combo
        #this is currently logically flawed, but i'll fix it later!
        #for example a crosslisted COS306/ELE206 would match ELE306    <-- fixed
        if len(q.split(" ")) == 2:
            qS = q.split(" ")
            classes = Course_Specific.objects.filter(dept__icontains=qS[0], num__icontains=qS[1])
            if (len(classes) > 0):
                #context = {'classes': classes}
                #return render(request, 'curves/results.html', context)
                for c in classes:
                    depts = c.dept.split("+")
                    print depts
                    nums = c.num.split("+")
                    print nums
                    for i in range(0, len(nums)):
                        if (depts[i] == qS[0].upper()) and (nums[i] == qS[1]):
                            return courseView(request, c.dept, c.num)

        #check if the search term is just a number?
        if len(q) <= 4:
            classes = Course_Specific.objects.filter(num__icontains=q)
            if (len(classes) == 1):
                aClass = classes[0]
                return courseView(request, aClass.dept, aClass.num)
            if (len(classes) > 0):
                uniqueClasses = []
                for c in classes:
                    for u in uniqueClasses:
                        if u.dept == c.dept:
                            break
                    else:
                        uniqueClasses.append(c)
                context = {'classes': uniqueClasses}
                return render(request, 'curves/results.html', context)

        #check if search term is part of a class title?
        classes = Course_Specific.objects.filter(name__icontains=q)
        if (len(classes) == 1):
            aClass = classes[0]
            return courseView(request, aClass.dept, aClass.num)
        elif (len(classes) > 0):
            uniqueClasses = []
            for c in classes:
                print "hi"
                for u in uniqueClasses:
                    if u.dept == c.dept and u.num == c.num:
                        break
                else:
                    uniqueClasses.append(c)
            context = {'classes': uniqueClasses}
            return render(request, 'curves/results.html', context)
        else:
            context = {'query': q}
            return render (request, 'curves/invalid.html', context)
    else:
        return HttpResponse('Please submit a search term.')
    return HttpResponse(message)

def handler404(request):
    response = render(request, 'curves/404.html')
    response.status_code = 404
    return response
