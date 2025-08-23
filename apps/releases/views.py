from django.shortcuts import render, get_object_or_404
from django.http import FileResponse, Http404
from django.views.generic import View
from .models import Release


class ReleaseDownloadView(View):
    def get(self, request, pk):
        release = get_object_or_404(Release, pk=pk, is_active=True)
        
        if not release.file:
            raise Http404("Dosya bulunamadı")
        
        # İndirme sayısını artır
        release.download_count += 1
        release.save(update_fields=['download_count'])
        
        # Dosyayı servis et
        response = FileResponse(
            open(release.file.path, 'rb'),
            as_attachment=True,
            filename=f"{release.application.slug}-{release.version}.exe"
        )
        
        return response
