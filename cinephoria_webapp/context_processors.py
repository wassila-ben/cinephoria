from .models import Cinema

def cinemas_context(request):
    cinemas = Cinema.objects.all()
    selected_cinema_id = request.session.get('cinema_id')
    selected_cinema = Cinema.objects.filter(id=selected_cinema_id).first() if selected_cinema_id else None

    return {
        'cinemas': cinemas,
        'cinema': selected_cinema or None,
    }
