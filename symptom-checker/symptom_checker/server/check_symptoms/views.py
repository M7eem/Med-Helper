import ujson
from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from symptom_checker.includes.description_parsing import get_diseases, get_symptoms

VALID_MIN_FREQUENCIES = [
    "Very rare",
    "Occasional",
    "Frequent",
    "Very frequent",
    "Obligate",
]

VALID_SORT_METHODS = ["num_matched_symptoms", "first_matched_symptom"]

MAX_DESCRIPTION_LENGTH = 4096


# disable CRSF validation
@csrf_exempt
def index(request):
    if request.method == "POST":

        description = request.POST.get("description")

        # check that description is not empty
        if description is None or description == "":

            return HttpResponse(
                ujson.dumps({"error": "nonempty 'description' field required."}),
                content_type="application/json",
                status=400,
            )

        # check that description is not too long
        if len(description) > MAX_DESCRIPTION_LENGTH:

            return HttpResponse(
                ujson.dumps(
                    {
                        "error": f"description larger than maximum length ({MAX_DESCRIPTION_LENGTH})"
                    }
                ),
                content_type="application/json",
                status=400,
            )

        min_frequency = request.POST.get("min_frequency")
        sort_method = request.POST.get("sort_method")

        # set default min_frequency
        if min_frequency is None:
            min_frequency = "Very rare"

        if min_frequency not in VALID_MIN_FREQUENCIES:

            error = f"invalid 'min_frequency' field. Possible options in order of exclusivity: {VALID_MIN_FREQUENCIES}"

            return HttpResponse(
                ujson.dumps({"error": error}),
                content_type="application/json",
                status=400,
            )

        # check sorting method
        if sort_method not in VALID_SORT_METHODS:

            error = (
                f"invalid 'sort_method' field. Possible options: {VALID_SORT_METHODS}"
            )

            return HttpResponse(
                ujson.dumps({"error": error}),
                content_type="application/json",
                status=400,
            )

        try:

            symptoms = get_symptoms(description)
            diseases = get_diseases(symptoms, min_frequency, sort_method)

        except:

            return HttpResponse(
                ujson.dumps({"error": "Internal error."}),
                content_type="application/json",
                status=500,
            )

        return HttpResponse(
            ujson.dumps({"symptoms": symptoms, "diseases": diseases}),
            content_type="application/json",
        )

    else:
        return HttpResponse(
            ujson.dumps(
                {"error": "Invalid request method. Only POST requests allowed."}
            ),
            content_type="application/json",
            status=405,
        )
