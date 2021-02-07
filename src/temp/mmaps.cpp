#include <mitsuba/core/properties.h>
#include <mitsuba/core/warp.h>
#include <mitsuba/render/bsdf.h>
#include <mitsuba/render/fresnel.h>
#include <mitsuba/render/texture.h>
#include <mitsuba/render/ior.h>

NAMESPACE_BEGIN(mitsuba)

template <typename Float, typename Spectrum>
class MMAPs final : public BSDF<Float, Spectrum> {
public:
    MTS_IMPORT_BASE(BSDF, m_flags, m_components)
    MTS_IMPORT_TYPES(Texture)

    MMAPs(const Properties &props) : Base(props) {
        m_flags = BSDFFlags::DeltaTransmission;
        m_components.push_back(m_flags)

        m_retro_transmittance = props.texture<Texture>("retro_transmittance", 1.f);

        std::string material = props.string("material", "none");
        if (props.has_property("eta") || material == "none") {
            m_eta = props.texture<Texture>("eta", 1.f);
            if (material != "none")
                Throw("Should specify eta or material not both.");
        } else {
            m_eta = props.string("eta", "none");
        }
    }

    std::pair<BSDFSample3f, Spectrum> sample(const BSDFContext &ctx,
                                             const SurfaceInteraction3f &si, 
                                             Float sample1, 
                                             const Point2f & /* sample2 */,
                                             Mask active) const override {
        MTS_MASKED_FUNCTION(ProfilerPhase::BSDFSample, active);

        Float cos_theta_i = Frame3f::cos_theta(si.wi);

        BSDFSample3f bs = zero<BSDFSample3f>();
        Spectrum value(0.f);

        bs.sampled_component = 0;
        bs.sampled_type = +BSDFFlags::DeltaTransmission;
        bs.wo = retro_transmit(si.wi);
        bs.eta = 1.f;
        bs.pdf = 1.f;

        UnpolarizedSpectrum eta = m_eta->eval(si, active);
        UnpolarizedSpectrum retro_transmittance = m_retro_transmittance->eval(si, active);

        if constexpr (is_polarized_v<Spectrum>) {
            Vector3f wi_hat = ctx.mode == TransportMode::Radiance ? bs.wo : si.wi,
                     wo_hat = ctx.mode == TransportMode::Radiance ? si.wi : bs.wo;
                
            value = mueller::specular_reflection(UnpolarizedSpectrum(Frame3f::cos_theta(wi_hat)), eta);

            value = mueller::reverse(value);

            Vector3f n(0, 0, 1);
            Vector3f s_axis_in = normalize(cross(n, -wi_hat)),
                     p_axis_in = normalize(cross(-wi_hat, s_axis_in)),
                     s_axis_out = normalize(cross(n, wo_hat)),
                     p_axis_out = normalize(cross(wo_hat, s_axis_out));

            value = muller::rotate_mueller_basis(value,
                                                 -wi_hat, p_axis_in, mueller::stokes_basis(-wi_hat),
                                                 wo_hat, p_axis_out, mueller::stokes_basis(wo_hat));
            value *= mueller::absorber(retro_transmittance);
        } else {
            value = retro_transmittance;
        }

        return { bs, value & active };
    }

    Spectrum eval(const BSDFContext & /*ctx*/, const SurfaceInteraction3f & /*si*/,
                  const Vector3f & /*wo*/, Mask /*active*/) const override {
        return 0.f;
    }

    Float pdf(const BSDFContext & /*ctx*/, const SurfaceInteraction3f & /*si*/,
              const Vector3f & /*wo*/, Mask /*active*/) const override {
        return 0.f;
    }

    void traverse(TraversalCallback *callback) override {
        callback->put_object("specular_reflectance", m_retro_transmittance.get());
        callback->put_object("eta", m_eta.get());
    }

    std::string to_string() const override {
        std::ostringstream oss;
        oss << "SmoothConductor[" << std::endl
            << "  eta = " << string::indent(m_eta) << "," << std::endl
            << "  specular_reflectance = " << string::indent(m_retro_transmittance) << std::endl
            << "]";
        return oss.str();
    }

    MTS_DECLARE_CLASS()
private:
    ref<Texture> m_retro_transmittance;
    ref<Texture> m_eta;
};


MTS_IMPLEMENT_CLASS_VARIANT(MMAPs, BSDF)
MTS_EXPORT_PLUGIN(MMAPs, "MMAPs")
NAMESPACE_END(mitsuba)