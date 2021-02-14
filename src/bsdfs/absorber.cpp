#include <mitsuba/core/properties.h>
#include <mitsuba/core/spectrum.h>
#include <mitsuba/core/bitmap.h>
#include <mitsuba/core/warp.h>
#include <mitsuba/render/bsdf.h>
#include <mitsuba/render/texture.h>

NAMESPACE_BEGIN(mitsuba)

template <typename Float, typename Spectrum>
class Absorber final : public BSDF<Float, Spectrum> {
public:
    MTS_IMPORT_BASE(BSDF, m_flags, m_components)
    MTS_IMPORT_TYPES(Texture)

    Absorber(const Properties &props) : Base(props) {

        m_components.push_back(m_flags);
    }

    std::pair<BSDFSample3f, Spectrum> sample(const BSDFContext &ctx,
                                             const SurfaceInteraction3f &si, 
                                             Float /* sample1 */,
                                             const Point2f &sample2,
                                             Mask active) const override {
        MTS_MASKED_FUNCTION(ProfilerPhase::EndpointSampleRay, active);

        Float cos_theta_i = Frame3f::cos_theta(si.wi);
        BSDFSample3f bs = zero<BSDFSample3f>();

        active &= cos_theta_i > 0.f;
        if (unlikely(none_or<false>(active) || 
                     !ctx.is_enabled(BSDFFlags::DiffuseReflection)))
            return { bs, 0.f };
        
    }

    void traverse(TraversalCallback *callback) override {
        callback->put_object("reflectance", m_reflectance.get());
    }

    std::string to_string() const override {
        std::ostringstream oss;
        oss << "Absorber[" << std::endl
            << "  reflectance = " << string::indent(m_reflectance) << std::endl;
            << "]";
        return oss.str();
    }
private:
    ref<Texture> m_reflectance;
    ref<Bitmap> m_bitmap;
};

MTS_IMPLEMENT_CLASS_VARIANT(Absorber, BSDF)
MTS_EXPORT_PLUGIN(Absorber, "Absorber material")
NAMESPACE_END(mitsuba)