from django.views.generic import ListView, DetailView, CreateView, TemplateView, UpdateView
from django.urls import reverse_lazy
from ..models import Blog, Review, Comment, User, Tag
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.db.models import Count
from ..forms import RegisterForm, BlogForm, UserProfileForm, ReviewForm
from django.db.models import Count, Avg


class BlogListView(ListView):
    model = Blog
    template_name = 'blogapp/blog_list.html'
    context_object_name = 'blogs'
    paginate_by = 3

    def get_queryset(self):
        queryset = super().get_queryset().select_related('author').prefetch_related('tags')
        tag_slug = self.request.GET.get('tag')
        if tag_slug:
            tag = get_object_or_404(Tag, name=tag_slug)
            queryset = queryset.filter(tags=tag)
        return queryset.order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['popular_tags'] = Tag.objects.annotate(num_blogs=Count('blog')).order_by('-num_blogs')[:10]
        tag_slug = self.request.GET.get('tag')
        if tag_slug:
            context['current_tag'] = get_object_or_404(Tag, name=tag_slug)
        
        return context


class BlogDetailView(DetailView):
    model = Blog
    template_name = 'blogapp/blog_detail.html'
    context_object_name = 'blog'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['related_blogs'] = Blog.objects.filter(
            tags__in=self.object.tags.all()
        ).exclude(pk=self.object.pk).distinct()[:3]
        return context


class BlogCreateView(LoginRequiredMixin, CreateView):
    model = Blog
    form_class = BlogForm
    template_name = 'blogapp/blog_form.html'

    def post(self, request, *args, **kwargs):
        # Copiamos request.POST para modificarlo
        post_data = request.POST.copy()

        # Convertimos 'tags' de "2,7" a ['2', '7']
        tags_str = post_data.get('tags', '')
        if tags_str:
            tag_list = [tag_id.strip() for tag_id in tags_str.split(',') if tag_id.strip().isdigit()]
            post_data.setlist('tags', tag_list)
        else:
            post_data.setlist('tags', [])

        # Reemplazamos request.POST con la modificada
        request.POST = post_data

        return super().post(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.author = self.request.user

        # Guardamos el objeto (ya con tags como lista)
        self.object = form.save()

        messages.success(self.request, '¡Blog creado exitosamente!')
        return super().form_valid(form)  # ahora que self.object existe

    def get_success_url(self):
        return reverse_lazy('blogapp:blog_detail', kwargs={'pk': self.object.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['all_tags'] = Tag.objects.all()
        return context


class ReviewCreateView(LoginRequiredMixin, CreateView):
    model = Review
    form_class = ReviewForm
    template_name = 'blogapp/review_form.html'

    def form_valid(self, form):
        # Obtenemos el blog correspondiente con el pk pasado en la URL
        blog = get_object_or_404(Blog, pk=self.kwargs['pk'])

        # Verificamos si el usuario ya ha hecho una reseña para este blog
        if Review.objects.filter(blog=blog, reviewer=self.request.user).exists():
            messages.error(self.request, 'Ya has enviado una reseña para este blog.')
            return redirect('blogapp:blog_detail', pk=blog.pk)

        # Si no hay reseña previa, asignamos al revisor (usuario actual)
        form.instance.reviewer = self.request.user
        form.instance.blog = blog

        messages.success(self.request, '¡Reseña enviada exitosamente!')
        return super().form_valid(form)

    def get_success_url(self):
        # Redirigimos al detalle del blog después de una reseña exitosa
        return reverse_lazy('blogapp:blog_detail', kwargs={'pk': self.kwargs['pk']})


class CommentCreateView(LoginRequiredMixin, CreateView):
    model = Comment
    fields = ['content']
    template_name = 'blogapp/comment_form.html'

    def form_valid(self, form):
        form.instance.commenter = self.request.user
        form.instance.review = get_object_or_404(Review, pk=self.kwargs['review_pk'])
        messages.success(self.request, '¡Comentario publicado!')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('blogapp:blog_detail', kwargs={'pk': self.kwargs['blog_pk']})


def register_view(request):
    if request.user.is_authenticated:
        return redirect('blogapp:blog_list')

    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, '¡Registro exitoso! Bienvenido/a')
            return redirect('blogapp:blog_list')
    else:
        form = RegisterForm()

    return render(request, 'blogapp/register.html', {
        'form': form,
        'title': 'Registro'
    })


def login_view(request):
    if request.user.is_authenticated:
        return redirect('blogapp:blog_list')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, f'Bienvenido/a de vuelta, {username}!')
            next_url = request.GET.get('next', 'blogapp:blog_list')
            return redirect(next_url)
        else:
            messages.error(request, 'Usuario o contraseña incorrectos')

    return render(request, 'blogapp/login.html', {
        'title': 'Iniciar Sesión'
    })


def logout_view(request):
    if request.user.is_authenticated:
        logout(request)
        messages.success(request, 'Has cerrado sesión correctamente')
    return redirect('blogapp:blog_list')


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'blogapp/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_blogs = Blog.objects.filter(author=self.request.user).order_by('-created_at')

        context.update({
            'blogs': user_blogs,
            'total_blogs': user_blogs.count(),
            'total_reviews': Review.objects.filter(reviewer=self.request.user).count(),
            'recent_activity': Review.objects.filter(
                reviewer=self.request.user
            ).select_related('blog').order_by('-created_at')[:5]
        })
        return context


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = UserProfileForm
    template_name = 'blogapp/profile_edit.html'
    success_url = reverse_lazy('blogapp:dashboard')

    def get_object(self):
        return self.request.user

    def form_valid(self, form):
        messages.success(self.request, 'Perfil actualizado correctamente')
        return super().form_valid(form)

class PopularBlogsView(ListView):
    model = Blog
    template_name = 'blogapp/blog_popular.html'
    context_object_name = 'blogs'
    paginate_by = 10

    def get_queryset(self):
        # Anotamos los blogs con el promedio de rating y número de comentarios
        queryset = Blog.objects.annotate(
            avg_rating=Avg('reviews__rating'),
            num_comments=Count('reviews__comments')
        ).order_by('-avg_rating', '-num_comments', '-created_at').select_related('author').prefetch_related('tags')
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['popular_tags'] = Tag.objects.annotate(num_blogs=Count('blog')).order_by('-num_blogs')[:10]
        return context